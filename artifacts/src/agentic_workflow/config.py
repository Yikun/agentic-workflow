"""配置读取与写入。"""

from __future__ import annotations

import json
from pathlib import Path

from .constants import CONFIG_DIR, CONFIG_FILE, MANIFEST_FILE
from .errors import ConfigError
from .models import AppConfig, Manifest


def get_config_path(repo_root: Path) -> Path:
    return repo_root / CONFIG_DIR / CONFIG_FILE


def get_manifest_path(repo_root: Path) -> Path:
    return repo_root / CONFIG_DIR / MANIFEST_FILE


def ensure_config_dir(repo_root: Path) -> Path:
    path = repo_root / CONFIG_DIR
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_or_create_config(repo_root: Path) -> AppConfig:
    config_path = get_config_path(repo_root)
    if not config_path.exists():
        config = AppConfig(repo_root=repo_root)
        save_config(config)
        return config

    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"配置文件 JSON 解析失败: {config_path}") from exc

    return AppConfig.from_dict(repo_root=repo_root, payload=payload)


def save_config(config: AppConfig) -> None:
    ensure_config_dir(config.repo_root)
    config_path = get_config_path(config.repo_root)
    config_path.write_text(
        json.dumps(config.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def load_manifest(repo_root: Path) -> Manifest | None:
    manifest_path = get_manifest_path(repo_root)
    if not manifest_path.exists():
        return None

    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"manifest JSON 解析失败: {manifest_path}") from exc

    return Manifest.from_dict(payload)


def save_manifest(repo_root: Path, manifest: Manifest) -> None:
    ensure_config_dir(repo_root)
    manifest_path = get_manifest_path(repo_root)
    manifest_path.write_text(
        json.dumps(manifest.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def delete_manifest(repo_root: Path) -> None:
    manifest_path = get_manifest_path(repo_root)
    if manifest_path.exists():
        manifest_path.unlink()
