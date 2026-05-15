# AGENTS.md — 项目协作规范

本文件适用于所有在此仓库中运行的 AI Agent 及人工贡献者。

## 分支与提交规范

- **禁止直接向 `main` 分支提交代码。** 所有代码变更必须通过 Pull Request 提交，并在合并前完成 Review。
- 每个 PR 应对应一个明确的 Issue 或任务，PR 描述中须注明关联的 Issue 编号（`Closes #xxx`）。
- 分支命名建议：`agentic/issue-{issue_number}` 或 `feat/{简短描述}`。
- **Agent 只提交 PR，不得自行合并（禁止 `gh pr merge`）。** 所有 PR 须由人工审核后方可合并。

## 提交前本地检查（Pre-commit）

在创建 PR 或推送代码前，**必须在本地通过以下检查**，不得跳过：

1. **Lint 检查**：`ruff check .`
2. **格式检查**：`ruff format --check .`
3. **类型检查**：`mypy docs/src`
4. **YAML 检查**：`yamllint .github/workflows`

所有检查均须以零错误退出（exit code 0）方可推送。

## Agent 文件归属矩阵

每个 Agent 只读写其负责的文件，不得越界操作：

| Agent              | 读取                                           | 写入                           |
|--------------------|------------------------------------------------|--------------------------------|
| requirements       | `docs/00-user-brief.md`                        | `docs/01-requirements.md`      |
| requirements-qa    | `docs/01-requirements.md`                      | `docs/01-requirements-qa.md`   |
| architect          | `docs/01-requirements.md`                      | `docs/02-architecture.md`      |
| architect-qa       | `docs/01-requirements.md`, `docs/02-architecture.md` | `docs/02-architecture-qa.md` |
| coder              | `docs/01-requirements.md`, `docs/02-architecture.md` | `docs/src/**`                |
| testcase-dev       | `docs/01-requirements.md`, `docs/02-architecture.md`, `docs/src/**` | `docs/03-test-cases.md` |
| tester             | `docs/03-test-cases.md`, `docs/src/**`         | `docs/04-report.md`            |

**规则：**
- Agent **不得**修改上表"写入"列以外的 `docs/` 文件。
- Agent **不得**直接操作 `agentic-issues/`（归档由 03-tester 工作流负责）。
- 工作流脚本（`.github/workflows/`）可写入 `docs/00-user-brief.md` 作为管道输入准备，但**不得**通过 shell 直接覆写其他 `docs/*.md` 文件。

## `docs/` 工作目录说明

`docs/` 是管道的当前工作区，每次 Issue 运行时被覆写。包含：

| 文件 | 描述 |
|------|------|
| `docs/00-user-brief.md` | 当前 Issue 的用户需求（由工作流从 GitHub Issue 获取并写入） |
| `docs/01-requirements.md` | 需求文档（requirements agent 输出） |
| `docs/01-requirements-qa.md` | 需求 QA（requirements-qa agent 输出） |
| `docs/02-architecture.md` | 架构文档（architect agent 输出） |
| `docs/02-architecture-qa.md` | 架构 QA（architect-qa agent 输出） |
| `docs/03-test-cases.md` | 验收用例（testcase-dev agent 输出） |
| `docs/04-report.md` | 测试报告（tester agent 输出） |
| `docs/src/` | 生产代码（coder agent 输出） |

## Issue 归档格式

每个 Issue 完成后，`03-tester` 工作流将所有产物归档至：

```
agentic-issues/issue-{n}-{title-slug}/
├── 00-user-brief.md
├── 01-requirements.md
├── 01-requirements-qa.md
├── 02-architecture.md
├── 02-architecture-qa.md
├── 03-test-cases.md
├── 04-report.md
└── src/
```

其中 `{title-slug}` 为 Issue 标题的小写连字符格式，限 40 字符。

## Agent 行为约束

- Agent 不得直接调用 `git push` 向 `main` 推送，只能推送到 feature 分支。
- Agent 在生成代码后，须在本地执行上述 lint/格式检查并确认通过，再提交到 feature 分支。
- Agent 不得绕过 FR-04 定义的人工审批门禁（`/approve` 评论）自动推进阶段。
- **Agent 只提交 PR，不得执行 `gh pr merge`。**

## 重要提示

- 如果测试出现问题，请在 `docs/` 目录先修改对应的设计文档，然后再进行开发和测试。
