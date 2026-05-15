# AGENTS.md — 项目协作规范

本文件适用于所有在此仓库中运行的 AI Agent 及人工贡献者。

## 目录结构

```
/
├── .github/workflows/          # GitHub Actions 工作流
│   ├── agents/                 # Agent 提示文件（与 workflow 同目录）
│   │   ├── requirements/CLAUDE.md
│   │   ├── requirements-qa/CLAUDE.md
│   │   ├── architect/CLAUDE.md
│   │   ├── architect-qa/CLAUDE.md
│   │   ├── coder/CLAUDE.md
│   │   ├── testcase-dev/CLAUDE.md
│   │   └── tester/CLAUDE.md
│   └── *.yml
├── agentic-issues/             # 每个 Issue 独立的工作目录（运行时写入）
│   └── issue-{n}-{slug}/       # 每次 pipeline 运行的隔离目录
│       ├── 00-user-brief.md
│       ├── 01-requirements.md
│       ├── 01-requirements-qa.md
│       ├── 02-architecture.md
│       ├── 02-architecture-qa.md
│       ├── 03-test-cases.md
│       ├── 04-report.md
│       └── src/                # 该 Issue 生成的代码
├── src/                        # Python 验收测试框架包（静态，不随 Issue 变更）
│   └── agentic_workflow/
└── docs/                       # 本项目静态文档
```

## 每 Issue 工作目录（ISSUE_DIR）

每次流水线运行时，Workflow 在运行时动态计算工作目录：

```bash
ISSUE_NO="${{ inputs.issue_number }}"
TITLE=$(gh issue view "$ISSUE_NO" -R "${{ github.repository }}" --json title --jq '.title')
SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' \
  | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' \
  | sed 's/^-//;s/-$//' | cut -c1-40)
ISSUE_DIR="agentic-issues/issue-${ISSUE_NO}-${SLUG}"
mkdir -p "$ISSUE_DIR"
```

Agent 提示文件（CLAUDE.md）内部使用 `artifacts/` 作为占位符，Workflow 在调用时通过 `sed` 替换为实际路径：

```bash
PROMPT=$(sed "s|artifacts/|${ISSUE_DIR}/|g" .github/workflows/agents/requirements/CLAUDE.md)
~/.opencode/bin/opencode run --dangerously-skip-permissions -m alibaba-cn/qwen-plus "$PROMPT"
```

## 文件归属矩阵

每个 Agent **只能写入**自己职责范围内的文件：

| Agent | 可写文件 |
|-------|---------|
| requirements | `$ISSUE_DIR/00-user-brief.md`（只读）, `$ISSUE_DIR/01-requirements.md` |
| requirements-qa | `$ISSUE_DIR/01-requirements-qa.md` |
| architect | `$ISSUE_DIR/02-architecture.md` |
| architect-qa | `$ISSUE_DIR/02-architecture-qa.md` |
| coder | `$ISSUE_DIR/src/`（含 README.md、DECISIONS.md） |
| testcase-dev | `$ISSUE_DIR/03-test-cases.md` |
| tester | `$ISSUE_DIR/04-report.md` |

**任何 Agent 不得修改其他阶段的产物。**

## 分支与提交规范

- **禁止直接向 `main` 分支提交代码。** 所有代码变更必须通过 Pull Request 提交。
- 每个 PR 应对应一个明确的 Issue，PR 描述中须注明关联的 Issue 编号（`Closes #xxx`）。
- 分支命名：`agentic/issue-{issue_number}`（Agent 自动创建）或 `feat/{简短描述}`。
- **禁止 Agent 执行 `gh pr merge`。** Agent 只提交 PR，由人工合并。

## 提交前本地检查（Pre-commit）

在创建 PR 或推送代码前，**必须在本地通过以下检查**：

```bash
source .venv/bin/activate
ruff check .
ruff format --check .
mypy src
yamllint -d '{extends: default, rules: {document-start: disable, truthy: disable, line-length: {max: 120}}}' .github/workflows
```

所有检查均须以零错误退出（exit code 0）方可推送。

## Agent 行为约束

- Agent 不得直接调用 `git push` 向 `main` 推送，只能推送到 feature 分支。
- Agent 在生成代码后，须在本地执行上述 lint/格式检查并确认通过，再提交到 feature 分支。
- Agent 不得绕过 FR-04 定义的人工审批门禁（`/approve` 评论）自动推进阶段。
- Agent 禁止使用 `gh pr merge`，只提交 PR 等待人工审核。
