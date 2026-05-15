"""自定义异常类型。"""

from __future__ import annotations


class AgenticWorkflowError(RuntimeError):
    """业务层通用异常。"""


class ConfigError(AgenticWorkflowError):
    """配置文件错误。"""


class InstallError(AgenticWorkflowError):
    """安装流程错误。"""
