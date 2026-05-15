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

## 产物归档规范（Artifact Ownership）

每个 Agent 只负责写入自己职责范围内的文件，不得越权写入其他 Agent 或 Workflow 的产物。

| 文件路径 | 写入方 | 说明 |
|---|---|---|
| `artifacts/00-user-brief.md` | requirements agent | agent 从 GitHub Issue 获取内容后写入 |
| `artifacts/01-requirements.md` | requirements agent | 需求分析报告 |
| `artifacts/01-requirements-qa.md` | requirements-qa agent | 需求 QA 审查报告 |
| `artifacts/02-architecture.md` | architect agent | 架构设计文档 |
| `artifacts/02-architecture-qa.md` | architect-qa agent | 架构 QA 报告 |
| `artifacts/03-test-cases.md` | testcase-dev agent | 验收测试用例 |
| `artifacts/04-report.md` | tester agent | 验收测试报告 |
| `agentic-issues/{n}/` | Stage 3 workflow（git commit） | Stage 3 完成后自动归档本 Issue 全部产物；各 Issue 归档互不覆盖 |

**禁止项（任何角色均不得违反）**：
- Workflow 脚本（`.github/workflows/`）**不得**通过 shell 直接向 `artifacts/` 写入文件内容，只允许 `git add/commit` 提交 agent 已生成的产物。
- Agent **不得**修改 `.github/workflows/`、`agents/`、`AGENTS.md`、`README.md` 等项目配置文件。
- Agent **不得**修改其他 Agent 职责范围内的产物文件。
- Agent 和 Workflow **均不得**修改被流水线处理的目标项目的源文件（即本仓库之外的任何文件）。

## Agent 行为约束

- Agent 不得直接调用 `git push` 向 `main` 推送，只能推送到 feature 分支。
- Agent 仅可提交并推送 PR，不得自行执行 PR 合并（例如 `gh pr merge`）；**必须由人工完成合并**。
- Agent 在生成代码后，须在本地执行上述 lint/格式检查并确认通过，再提交到 feature 分支。
- Agent 不得绕过 FR-04 定义的人工审批门禁（`/approve` 评论）自动推进阶段。

## 重要提示
- 如果测试出现问题，请在artifacts目录先修改对应的设计文档、开发、测试，然后再进行