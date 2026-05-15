"""命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import load_or_create_config, save_config
from .constants import VERSION
from .errors import AgenticWorkflowError
from .installer import (
    install_workflows,
    list_expected_workflows,
    uninstall_workflows,
    upgrade_workflows,
    validate_installation,
)
from .models import AppConfig


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentic-workflow",
        description="安装并管理 Agentic Workflow 的 GitHub Actions 文件",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="仓库根目录，默认当前目录",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init-config", help="初始化默认配置")

    install_parser = subparsers.add_parser("install", help="安装工作流文件")
    install_parser.add_argument(
        "--dry-run", action="store_true", help="仅打印将要写入的文件"
    )

    upgrade_parser = subparsers.add_parser("upgrade", help="升级已安装工作流文件")
    upgrade_parser.add_argument(
        "--dry-run", action="store_true", help="仅打印将要写入的文件"
    )

    uninstall_parser = subparsers.add_parser("uninstall", help="卸载工作流文件")
    uninstall_parser.add_argument(
        "--keep-config", action="store_true", help="卸载时保留配置目录"
    )
    uninstall_parser.add_argument(
        "--dry-run", action="store_true", help="仅打印将要删除的文件"
    )

    subparsers.add_parser("validate", help="校验安装结果")
    subparsers.add_parser("list-workflows", help="列出会生成的工作流文件")
    subparsers.add_parser("show-config", help="展示当前配置")

    return parser


def _repo_root(path: str) -> Path:
    return Path(path).expanduser().resolve()


def _load_config(path: Path) -> AppConfig:
    return load_or_create_config(path)


def _print_lines(title: str, lines: list[str]) -> None:
    print(title)
    if not lines:
        print("- 无")
        return
    for line in lines:
        print(f"- {line}")


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    repo_root = _repo_root(args.repo_root)
    config = _load_config(repo_root)

    try:
        if args.command == "init-config":
            save_config(config)
            print("已初始化配置文件。")
            return 0

        if args.command == "install":
            written = install_workflows(config=config, dry_run=args.dry_run)
            _print_lines("安装/更新的文件:", written)
            return 0

        if args.command == "upgrade":
            written = upgrade_workflows(config=config, dry_run=args.dry_run)
            _print_lines("升级写入的文件:", written)
            return 0

        if args.command == "uninstall":
            removed = uninstall_workflows(
                config=config,
                keep_config=args.keep_config,
                dry_run=args.dry_run,
            )
            _print_lines("删除的文件:", removed)
            return 0

        if args.command == "validate":
            missing = validate_installation(config)
            if missing:
                _print_lines("缺失文件:", missing)
                return 2
            print("安装校验通过。")
            return 0

        if args.command == "list-workflows":
            _print_lines("预期工作流文件:", list_expected_workflows())
            return 0

        if args.command == "show-config":
            print(f"版本: {VERSION}")
            print(f"仓库根目录: {repo_root}")
            print(f"默认分支: {config.default_branch}")
            print(f"Runner: {config.runner}")
            print(f"语言: {config.language}")
            return 0

        parser.error(f"未知命令: {args.command}")
        return 2

    except AgenticWorkflowError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
