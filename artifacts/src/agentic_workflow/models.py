"""数据模型定义。"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .constants import DEFAULT_BRANCH, DEFAULT_LANGUAGE, DEFAULT_RUNNER


@dataclass(slots=True)
class AppConfig:
    """CLI 运行配置。"""

    repo_root: Path
    default_branch: str = DEFAULT_BRANCH
    runner: str = DEFAULT_RUNNER
    language: str = DEFAULT_LANGUAGE

    @classmethod
    def from_dict(cls, repo_root: Path, payload: dict[str, Any]) -> "AppConfig":
        return cls(
            repo_root=repo_root,
            default_branch=str(payload.get("default_branch", DEFAULT_BRANCH)),
            runner=str(payload.get("runner", DEFAULT_RUNNER)),
            language=str(payload.get("language", DEFAULT_LANGUAGE)),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "default_branch": self.default_branch,
            "runner": self.runner,
            "language": self.language,
        }


@dataclass(slots=True)
class Manifest:
    """记录安装产物，便于升级和卸载。"""

    version: str
    workflow_version: str
    files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "workflow_version": self.workflow_version,
            "files": self.files,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Manifest":
        version = str(payload.get("version", "0.0.0"))
        workflow_version = str(payload.get("workflow_version", "unknown"))
        files = [str(item) for item in payload.get("files", [])]
        return cls(version=version, workflow_version=workflow_version, files=files)
