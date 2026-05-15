# AGENTS.md — 项目协作规范

本文件适用于所有在此仓库中运行的 AI Agent 及人工贡献者。

## 分支与提交规范

- **禁止直接向 `main` 分支提交代码。** 所有代码变更必须通过 Pull Request 提交，并在合并前完成 Review。
- 每个 PR 应对应一个明确的 Issue 或任务，PR 描述中须注明关联的 Issue 编号（`Closes #xxx`）。
- 分支命名建议：`agentic/issue-{issue_number}` 或 `feat/{简短描述}`。

## 提交前本地检查（Pre-commit）

在创建 PR 或推送代码前，**必须在本地通过以下检查**，不得跳过：

1. **Lint 检查**（根据项目语言选择对应工具，例如）：
   - Python：`ruff check .` 或 `flake8`
   - JavaScript/TypeScript：`eslint .`
   - YAML：`yamllint .`
2. **格式检查**（例如）：
   - Python：`ruff format --check .` 或 `black --check .`
3. **类型检查**（如适用，例如）：
   - Python：`mypy .`
   - TypeScript：`tsc --noEmit`

所有检查均须以零错误退出（exit code 0）方可推送。

## Agent 行为约束

- Agent 不得直接调用 `git push` 向 `main` 推送，只能推送到 feature 分支。
- Agent 在生成代码后，须在本地执行上述 lint/格式检查并确认通过，再提交到 feature 分支。
- Agent 不得修改 `artifacts/01-requirements.md`（需求文档由 requirements agent 负责）。
- Agent 不得绕过 FR-04 定义的人工审批门禁（`/approve` 评论）自动推进阶段。

## 重要提示
- 如果测试出现问题，请在artifacts目录先修改对应的设计文档、开发、测试，然后再进行