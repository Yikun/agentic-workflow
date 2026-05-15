# agentic-workflow

以 GitHub Issue 为驱动入口、GitHub Actions 为调度引擎、多专职 AI Agent 协作执行的端到端自动化软件开发流水线。

---

## 三层模型：Workflow / Agent / Artifact

```
GitHub Issue（需求输入）
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                  GitHub Actions Workflow                      │
│  .github/workflows/*.yml                                     │
│  ─ 负责：触发条件、阶段门禁、串联调度、向 Issue 发布评论      │
│  ─ 不含业务逻辑，只负责"什么时候跑、跑什么、结果发哪里"      │
└──────────────────┬──────────────────────────────────────────┘
                   │ 调用
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                      AI Agent                                 │
│  .github/workflows/agents/<name>/CLAUDE.md                   │
│  ─ 每个 Agent 持有一份 CLAUDE.md，定义：角色、输入、输出、规则│
│  ─ 由 Workflow 步骤中的 opencode CLI 调用执行                   │
│  ─ 只读取 / 写入 agentic-issues/issue-{n}-{slug}/，不感知 GitHub 事件│
└──────────────────┬──────────────────────────────────────────┘
                   │ 读写
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                      Artifact                                 │
│  agentic-issues/issue-{n}-{slug}/*.md  /  src/               │
│  ─ 唯一的跨阶段信息载体，提交到 git 实现持久化                │
│  ─ 每个 Issue 拥有独立隔离的工作目录                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 流水线阶段与三者对应关系

| 阶段 | Workflow 文件 | 调用的 Agent | 输入 Artifact | 输出 Artifact |
|------|--------------|-------------|--------------|--------------|
| 1 需求分析 | `01-requirements.yml` | `agents/requirements/` | Issue 内容 | `$ISSUE_DIR/01-requirements.md` |
| 1b 需求 QA | `01-requirements-qa.yml` | `agents/requirements-qa/` | `$ISSUE_DIR/01-requirements.md` | `$ISSUE_DIR/01-requirements-qa.md` |
| ⛩ 阶段门禁 | `02-approve-gate.yml` | — | Issue `/approve` 评论 | 触发下一阶段 |
| 2 架构设计 | `02-architect.yml` | `agents/architect/` | `$ISSUE_DIR/01-requirements.md` | `$ISSUE_DIR/02-architecture.md` |
| 2b 架构 QA | `02-architect-qa.yml` | `agents/architect-qa/` | `$ISSUE_DIR/02-architecture.md` | `$ISSUE_DIR/02-architecture-qa.md` |
| 2c 编码 | `02-coder.yml` | `agents/coder/` | `$ISSUE_DIR/01-requirements.md` + `02-architecture.md` | `$ISSUE_DIR/src/` + PR |
| 2d 测试用例 | `02-testcase-dev.yml` | `agents/testcase-dev/` | `$ISSUE_DIR/src/` + `01-requirements.md` | `$ISSUE_DIR/03-test-cases.md` |
| ⛩ CI 门禁 | `03-ci-gate.yml` | — | PR Required CI 状态 | 触发下一阶段 |
| 3 验收测试 | `03-tester.yml` | `agents/tester/` | `$ISSUE_DIR/03-test-cases.md` + `$ISSUE_DIR/src/` | `$ISSUE_DIR/04-report.md` |

---

## 阶段门禁规则

**阶段一 → 二**：Issue 作者在 Issue 下评论精确内容 `/approve`（前后空白忽略，大小写敏感）。任何人编辑或删除该评论（`02-approve-invalidate.yml`）会立即失效并取消正在运行的阶段二流程。

**阶段二 → 三**：PR 上全部 Required CI 检查均为 `success`。未配置 Required 检查时视为阻断（不允许越级）。

---

## 目录结构

```
.github/workflows/              # GitHub Actions Workflow 文件（调度层）
  agents/                       # AI Agent 指令文件 CLAUDE.md（与 workflow 同目录）
agentic-issues/                 # 每个 Issue 的独立工作目录（运行时创建）
  issue-{n}-{slug}/             # 每次 pipeline 运行的隔离目录
    00-user-brief.md            # 用户原始需求
    01-requirements.md          # 需求文档
    01-requirements-qa.md       # 需求 QA 报告
    02-architecture.md          # 架构设计文档
    02-architecture-qa.md       # 架构 QA 报告
    03-test-cases.md            # 验收测试用例
    04-report.md                # 测试报告
    src/                        # 该 Issue 生成的源代码
src/                            # Python 验收测试框架包（静态）
docs/                           # 本项目静态文档
```

**设计原则**：每个 GitHub Issue 拥有完全隔离的工作目录，多个 Issue 并行运行互不干扰。

---

## 快速开始

1. 创建一个 GitHub Issue，描述需求。
2. 手动触发 `01-requirements.yml`，输入该 Issue 的编号。
3. 等待阶段一完成后，在对应 Issue 评论 `/approve`。
4. 后续阶段自动串联执行，产物写入 `agentic-issues/issue-{n}-{slug}/`，最终在 Issue 发布测试报告。

