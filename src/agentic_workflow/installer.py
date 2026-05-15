"""安装、升级、卸载核心实现。"""

from __future__ import annotations

from pathlib import Path

from .config import delete_manifest, load_manifest, save_manifest
from .constants import VERSION, WORKFLOW_VERSION
from .errors import InstallError
from .models import AppConfig, Manifest
from .templates import workflow_templates


WORKFLOW_DIR = Path(".github/workflows")


def _absolute(repo_root: Path, relative: str) -> Path:
    return repo_root / relative


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def install_workflows(config: AppConfig, dry_run: bool = False) -> list[str]:
    templates = workflow_templates(
        runner=config.runner,
        default_branch=config.default_branch,
    )
    written: list[str] = []

    for file_name, content in templates.items():
        relative = str(WORKFLOW_DIR / file_name)
        target = _absolute(config.repo_root, relative)
        if not dry_run:
            _write_text(target, content)
        written.append(relative)

    if not dry_run:
        save_manifest(
            config.repo_root,
            Manifest(
                version=VERSION,
                workflow_version=WORKFLOW_VERSION,
                files=written,
            ),
        )

    return written


def upgrade_workflows(config: AppConfig, dry_run: bool = False) -> list[str]:
    existing = load_manifest(config.repo_root)
    if existing is None:
        raise InstallError("未检测到已安装记录，无法执行升级。请先执行 install。")
    return install_workflows(config=config, dry_run=dry_run)


def uninstall_workflows(
    config: AppConfig, keep_config: bool = False, dry_run: bool = False
) -> list[str]:
    manifest = load_manifest(config.repo_root)
    if manifest is None:
        raise InstallError("未检测到 manifest，无法判断要卸载的文件。")

    removed: list[str] = []
    for relative in manifest.files:
        target = _absolute(config.repo_root, relative)
        if target.exists():
            if not dry_run:
                target.unlink()
            removed.append(relative)

    if not dry_run:
        delete_manifest(config.repo_root)
        if not keep_config:
            config_dir = config.repo_root / ".agentic-workflow"
            if config_dir.exists():
                remaining = list(config_dir.iterdir())
                if not remaining:
                    config_dir.rmdir()

    return removed


def validate_installation(config: AppConfig) -> list[str]:
    manifest = load_manifest(config.repo_root)
    if manifest is None:
        raise InstallError("未找到 manifest，请先执行 install。")

    missing: list[str] = []
    for relative in manifest.files:
        target = _absolute(config.repo_root, relative)
        if not target.exists():
            missing.append(relative)

    return missing


def list_expected_workflows() -> list[str]:
    templates = workflow_templates()
    return [str(WORKFLOW_DIR / name) for name in templates]
