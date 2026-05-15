# 系统架构设计文档

文档版本：1.0
编写日期：2026-05-15
编写人：Architect Agent
输入来源：artifacts/01-requirements.md

---

### 1. System overview

本系统是一套以 GitHub Issue 为驱动核心、以 GitHub Actions 为自动化引擎、以多专职 Agent 分工协作为执行模型的端到端 Agentic Workflow。

系统将单个 GitHub Issue 所描述的需求，经三个顺序阶段自动转化为：
- **阶段一（需求分析）**：结构化需求文档 + QA 审查报告，以 Issue 评论形式发布供用户审阅。
- **阶段二（架构设计与编码）**：架构设计文档 + 交付代码（存入 `artifacts/src/`）+ Pull Request，CI 通过后自动推进。
- **阶段三（验收测试）**：逐条执行测试用例，汇总写入测试报告，结论发布至 Issue。

每个阶段由明确的阶段门禁控制推进：阶段一→二须满足 `/approve` 人工批准条件；阶段二→三须满足 PR 上全部 Required CI 检查为成功状态。门禁条件不满足时，流程不得越级推进。

整个系统不引入独立部署服务，所有状态存储于 GitHub（Issue/PR 评论、分支、仓库文件），所有产物以 Markdown 文件形式存储于仓库 `artifacts/` 目录下。

---

### 2. Component breakdown

#### 2.1 外部交互层

| 组件 | 职责 |
|------|------|
| **GitHub Issue** | 系统唯一入口；承载原始需求输入（Issue 正文）；作为阶段性产出的发布渠道（评论）；接收用户 `/approve` 批准信号 |
| **GitHub Pull Request** | 代码交付载体；CI 状态检查挂载点；第二阶段完成的可追溯证明 |
| **GitHub Actions Workflow** | 各阶段及子阶段的自动化触发与调度宿主；每个阶段或子阶段对应一个独立 Workflow 文件 |

**Workflow 文件清单**（最少须创建，存储于 `.github/workflows/`）：

| 文件名 | 触发事件 | 负责的 Agent / 步骤 |
|--------|---------|-------------------|
| `01-requirements.yml` | `workflow_dispatch`（入参：`issue_number`） | requirements Agent |
| `01-requirements-qa.yml` | `workflow_dispatch`（由 requirements 成功后触发） | requirements-qa Agent |
| `02-approve-gate.yml` | `issue_comment.created` | 人工审批门禁校验，触发阶段二 |
| `02-approve-invalidate.yml` | `issue_comment.edited`、`issue_comment.deleted` | 批准失效检测，取消正在运行的阶段二 |
| `02-architect.yml` | `workflow_dispatch`（由 approve-gate 触发） | architect Agent |
| `02-architect-qa.yml` | `workflow_dispatch`（由 architect 成功后触发） | architect-qa Agent |
| `02-coder.yml` | `workflow_dispatch`（由 architect-qa 通过后触发） | coder Agent |
| `02-testcase-dev.yml` | `workflow_dispatch`（由 coder 成功且 PR 创建后触发） | testcase-dev Agent |
| `03-ci-gate.yml` | `check_suite.completed` | CI 状态门禁校验，触发阶段三 |
| `03-tester.yml` | `workflow_dispatch`（由 ci-gate 通过后触发） | tester Agent |

#### 2.2 Agent 执行层

| Agent | 阶段 | 职责边界 |
|-------|------|---------|
| **requirements** | 阶段一 | 从 Issue 读取原始需求描述，输出初稿需求文档 `artifacts/01-requirements.md` |
| **requirements-qa** | 阶段一 | 审查 `01-requirements.md`，输出 QA 审查报告；若发现阻断性问题则终止流程 |
| **architect** | 阶段二 | 读取已批准需求文档，输出架构设计文档 `artifacts/02-architecture.md` |
| **architect-qa** | 阶段二（architect 之后） | 审查 `02-architecture.md` 及 `01-requirements.md`，输出架构 QA 报告 `artifacts/02-architecture-qa.md`；若发现 Critical 或 Contradiction 问题则阻断流程，等待修复后重新触发 |
| **coder** | 阶段二 | 读取需求文档与架构文档，在 feature 分支上将代码产出写入 `artifacts/src/`，创建 PR |
| **testcase-dev** | 阶段二/三过渡（coder 完成后、tester 启动前） | 读取 `01-requirements.md` 及 `artifacts/src/`，输出 `artifacts/03-test-cases.md`，定义验收测试用例条目结构 |
| **tester** | 阶段三 | 逐条读取 `03-test-cases.md`，对 `artifacts/src/` 中代码执行验收测试，写入 `artifacts/04-report.md` |

#### 2.3 阶段门禁层

| 门禁 | 位置 | 判定逻辑 |
|------|------|---------|
| **人工审批门禁** | 阶段一→二 | 监听 Issue 评论事件，检查发布者身份（须为 Issue 原作者）及评论内容（去首尾空白后精确等于 `/approve`，大小写敏感），满足条件的最早一条评论方可触发阶段二 |
| **CI 状态门禁** | 阶段二→三 | 事件驱动校验 PR HEAD 提交上的 Required 状态检查；全部为 success 时方可触发阶段三；任一为非 success 或 Required 集合为空，均不得推进 |

#### 2.4 产物存储层

| 产物文件 | 写入方 | 读取方 |
|---------|-------|-------|
| `artifacts/01-requirements.md` | requirements agent | requirements-qa、architect、coder |
| `artifacts/01-requirements-qa.md` | requirements-qa agent | 人工审阅（Issue 评论摘要） |
| `artifacts/02-architecture.md` | architect agent | architect-qa、coder |
| `artifacts/02-architecture-qa.md` | architect-qa agent | 人工审阅（供 coder 参考） |
| `artifacts/03-test-cases.md` | testcase-dev agent | tester |
| `artifacts/04-report.md` | tester agent | 人工审阅（Issue 评论摘要） |
| `artifacts/src/` | coder agent | tester agent |

---

### 3. Technology choices

| 技术 | 选择理由 |
|------|---------|
| **GitHub Actions** | 与 GitHub Issue/PR 原生集成，事件驱动（`issues`、`issue_comment`、`pull_request`、`workflow_dispatch`），无需额外部署基础设施；满足 FR-12 |
| **GitHub Issues & PRs** | 提供天然的可追溯性、评论历史与状态检查能力，满足 NFR-01、FR-03、FR-07、FR-08、FR-10 |
| **Markdown 文件（仓库存储）** | 结构化、可版本控制、可审阅，满足 NFR-03、NFR-04；所有产物纳入 Git 历史便于审计 |
| **opencode GLM-5（Alibaba Cloud / DASHSCOPE）** | 符合 ASS-02、ASS-03 中对模型与密钥的预设；中文语言能力满足 FR-11 |
| **Feature 分支 + PR** | 隔离代码变更，支持 CI 检查挂载，满足 FR-06、FR-07、FR-08 |
| **YAML Workflow 文件** | GitHub Actions 原生格式，存储于 `.github/workflows/`，满足 FR-12 |

---

### 4. Interface contracts

#### 4.1 入口接口：Issue → 阶段一

- **触发方式**：手动触发（`workflow_dispatch`）并传入 `issue_number`（整数）
- **输入消费**：requirements agent 读取指定 Issue 的正文（title + body）
- **前置条件**：Issue 存在且可读；`DASHSCOPE_API_KEY` 已配置

#### 4.2 阶段一内部接口：Agent 间数据传递

- **requirements → requirements-qa**：通过共享文件 `artifacts/01-requirements.md`（Markdown，章节结构：Overview / FR / NFR / Assumptions / OOS）
- **requirements-qa → 用户**：发布 Issue 评论，内容包含 QA 审查报告摘要（Critical Issues 数量、Ambiguity 列表、Feasibility Concerns、Approved 列表）+ `artifacts/` 文件链接 + 下一步操作提示（认可请评论 `/approve`，需调整请直接回复评论说明修改点）
- **阻断行为**：requirements-qa 发现阻断性问题时，以非零退出码终止 Workflow；不进入等待态

#### 4.3 阶段门禁接口：/approve 评论 → 阶段二触发

- **监听事件**：`issue_comment.created` 事件（GitHub Actions 触发器）
- **合法性校验**：
  - 评论所属 Issue 与流程 Issue 编号一致
  - 评论作者 = Issue 原作者
  - `comment.body.strip() === "/approve"`（精确字符串比较，大小写敏感）
  - 若多条满足，取 `created_at` 最早一条
- **输出**：触发阶段二 Workflow（传递 `issue_number` 参数）

**批准失效机制（独立 Workflow）**：

除 `issue_comment.created` 监听外，须额外定义一个 Workflow 监听 `issue_comment.edited` 和 `issue_comment.deleted` 事件：
- 校验被操作的评论是否为已记录的批准评论（通过评论 ID 比对）
- 若是，则：取消正在运行的阶段二 Workflow（调用 Actions API `DELETE /repos/{owner}/{repo}/actions/runs/{run_id}`），并在 Issue 发布评论通知用户批准已失效、需重新发布 `/approve`
- 说明："立即失效"定义为"失效事件到达即重置状态并阻止后续步骤继续执行"；通过事件触发取消 + 每个阶段二子 Workflow 首步守卫校验共同保证

**状态存储约定**：

| 状态值 | 写入方 | 存储位置 | 读取方 |
|--------|--------|---------|--------|
| 批准评论 ID | `02-approve-gate.yml`（触发阶段二时写入） | 目标 Issue 上由系统发布的状态评论（固定标记：`<!-- state:approval -->`） |
| 阶段二活跃 run_id | 阶段二每个子 Workflow 在启动步骤写入 | 目标 Issue 标签：`stage2-active` + 状态评论字段 `stage2_run_id` |
| 当前阶段状态（可选） | 阶段二/三门禁 Workflow | 目标 Issue 状态评论字段 `stage`（如 `stage2`/`stage3`） |

- 读取方：`02-approve-invalidate.yml` 与阶段二各子 Workflow 的守卫步骤均必须按 `issue_number` 读取该 Issue 的状态评论与标签并做一致性校验，不得使用仓库级单值变量作为状态源。

- 并发控制：阶段二相关 Workflow 必须使用 `concurrency.group: stage2-${{ inputs.issue_number }}`，并在写状态时校验 `issue_number` 与当前 Workflow 上下文一致，避免同仓库多 Issue 并发互相覆盖。

- **阶段二失效控制规则**：阶段二每个子 Workflow 在首个步骤必须执行“批准有效性守卫检查”（重新拉取 `APPROVE_COMMENT_ID` 对应评论并校验仍满足 FR-04）；若校验失败则立即退出，不继续执行后续步骤。

#### 4.4 阶段二内部接口：Agent 间数据传递

- **architect 输入/输出**：读取 `artifacts/01-requirements.md`；写入 `artifacts/02-architecture.md`（章节：System overview / Component breakdown / Technology choices / Interface contracts / Data flow / Key decisions and trade-offs）
- **coder 输入**：读取 `artifacts/01-requirements.md` + `artifacts/02-architecture.md`
- **coder 输出**：在命名为 `agentic/issue-{issue_number}` 的 feature 分支上，将所有代码产物写入 `artifacts/src/`；创建 PR（目标基础分支：`main`）
- **PR 元数据**：标题与描述须以中文撰写（FR-11）；PR 描述须关联原 Issue（`Closes #issue_number`）

#### 4.5 阶段门禁接口：CI 状态 → 阶段三触发

- **触发事件**：监听 `check_suite.completed` 事件；仅在事件可映射到目标 PR 且 `event.head_sha == 目标 PR 当前 HEAD SHA` 时继续执行
- **Required 集合来源**：从目标 PR 的 base 分支保护规则或 Rulesets 读取 Required 状态检查集合（例如 `GET /repos/{owner}/{repo}/branches/{branch}/protection/required_status_checks` 或对应 Rulesets API）
- **比对算法**：以 Required 集合为基准，逐项检查其在目标 PR 当前 HEAD 提交上的结论是否为 `success`；禁止将“所有 check-runs”直接等同为 Required 集合
- **合法性校验**：
  - Required 检查集合非空
        - Required 集合逐项状态均为 `success`
- **输出**：在原 Issue 发布评论宣告进入阶段三；触发阶段三 Workflow

#### 4.6 阶段三内部接口：Agent 间数据传递

- **tester 输入**：`artifacts/03-test-cases.md`（条目结构：ID / 描述 / 前置条件 / 预期输出）+ `artifacts/src/`
- **tester 输出**：`artifacts/04-report.md`（结构：结果汇总表 / 逐条结果说明 / 失败详情分析 / 最终 PASS/FAIL 结论）
- **结论发布**：将最终结论及 `04-report.md` 链接以 Issue 评论形式发布

---

### 5. Data flow

```
[用户] 创建/指定 GitHub Issue
        │
        ▼
┌─────────────────────────────────────┐
│           阶段一：需求分析            │
│                                     │
│  Issue 正文                          │
│      │                              │
│      ▼                              │
│  requirements Agent                 │
│      │ 写入                          │
│      ▼                              │
│  artifacts/01-requirements.md       │
│      │ 读取                          │
│      ▼                              │
│  requirements-qa Agent              │
│      │ 写入                          │
│      ▼                              │
│  artifacts/01-requirements-qa.md    │
│      │                              │
│      ▼                              │
│  Issue 评论（需求文档摘要 + QA 报告） │
└─────────────────────────────────────┘
        │
        │ 等待 /approve 评论
        │（门禁：Issue 原作者、精确匹配、最早条）
        ▼
┌─────────────────────────────────────┐
│        阶段二：架构设计与编码          │
│                                     │
│  01-requirements.md                 │
│      │                              │
│      ▼                              │
│  architect Agent                    │
│      │ 写入                          │
│      ▼                              │
│  artifacts/02-architecture.md       │
│      │ 读取                          │
│      ▼                              │
│  architect-qa Agent                 │
│      │ 写入                          │
│      ▼                              │
│  artifacts/02-architecture-qa.md    │
│      │                              │
│      ├─ Critical/Contradiction > 0  │
│      │    → 阻断，Issue 评论通知     │
│      │    → 等待人工修复并重新触发   │
│      │                              │
│      ▼ 全部通过                      │
│  coder Agent                        │
│      │ 写入至 feature 分支            │
│      ▼                              │
│  artifacts/src/（代码产物）           │
│      │                              │
│      ▼                              │
│  Pull Request（agentic/issue-N→main）│
│      │                              │
│  [CI 自动化测试运行]                  │
└─────────────────────────────────────┘
        │
        │ 等待全部 Required CI 检查为 success
        │（门禁：非空集合 + 全部 success）
        ▼
┌─────────────────────────────────────┐
│           阶段三：验收测试            │
│                                     │
│  artifacts/03-test-cases.md         │
│      │ 逐条读取                       │
│      ▼                              │
│  tester Agent ← artifacts/src/      │
│      │ 写入                          │
│      ▼                              │
│  artifacts/04-report.md             │
│      │                              │
│      ▼                              │
│  Issue 评论（测试结论 + 报告链接）    │
└─────────────────────────────────────┘
        │
        ▼
[流程结束]
```

**跨组件数据流补充说明：**

- 所有 Agent 之间不直接通信；唯一的数据传递介质为仓库中的 Markdown 文件（单向顺序写入→读取）。
- GitHub Issue 评论承担双向职责：系统向用户的输出通道，以及用户向系统的控制信号通道（`/approve`）。
- feature 分支与 PR 既是代码交付载体，也是 CI 状态的挂载点，构成阶段二→三门禁的技术基础。
- `testcase-dev` Agent 的产出（`03-test-cases.md`）须在 coder 完成代码写入、PR 创建后由 `02-coder.yml` 以 `workflow_dispatch` 顺序触发 `02-testcase-dev.yml`，并在阶段三启动前完成写入（见决策五）；不得并行于 coder 或提前至架构阶段。

---

### 6. Key decisions and trade-offs

#### 决策一：以 GitHub Actions 作为唯一调度引擎

**决策**：不引入外部调度服务（如 Airflow、Temporal、自定义服务器），所有阶段触发逻辑均实现为 GitHub Actions Workflow 文件。

**优势**：
- 与 GitHub Issue/PR 事件原生集成，无需额外基础设施
- Workflow 文件纳入仓库版本控制，变更可审计
- 满足 FR-12 的强制要求

**代价**：
- GitHub Actions 为事件驱动的离散模型，需通过多 Workflow 协同（`issue_comment.edited/deleted` 失效事件监听 + 阶段二子 Workflow 首步守卫校验）来实现“立即失效”，实现复杂度较高
- 复杂的阶段门禁逻辑需在 Workflow YAML 内通过 GitHub API 调用实现，增加 Workflow 复杂度

---

#### 决策二：以仓库 Markdown 文件作为 Agent 间唯一数据总线

**决策**：Agent 间不直接传递数据，仅通过读写固定路径的 Markdown 文件交换状态。

**优势**：
- 所有中间产物可版本控制、可人工审阅，满足 NFR-01、NFR-03、NFR-04
- Agent 实现解耦：写入方与读取方无需感知对方存在
- 无需引入消息队列或共享数据库

**代价**：
- 文件路径与章节格式须在架构层严格约定，否则写入/读取不兼容
- 并发写入同一文件存在冲突风险（当前流程设计为顺序执行，可规避）

---

#### 决策三：以 Issue 评论作为人工审批信号

**决策**：使用 `/approve` 评论（精确字符串、发布者限制为 Issue 原作者）作为阶段一→二的唯一批准机制。

**优势**：
- 利用 GitHub 原生能力，无需自定义 UI
- 评论历史不可篡改（可追溯），满足 NFR-02
- 精确字符串匹配与作者限制有效防止误触发

**代价**：
- 依赖 `issue_comment` 事件触发，编辑/删除的「立即失效」需在事件处理层额外实现（如监听 `issue_comment.edited` 与 `issue_comment.deleted` 事件后重置阶段状态）
- 用户需了解特定评论格式，存在一定操作门槛

---

#### 决策四：以 PR Required CI 检查作为阶段二→三的自动门禁

**决策**：阶段三触发条件为 PR 上全部 Required 状态检查均为 success；空集合视为未通过。

**优势**：
- 利用 GitHub branch protection 机制，可配置性强
- 与 CI 工具无关（适配任何 CI provider）
- 空集合视为未通过消除了「无检查即放行」的安全漏洞，满足 NFR-02

**代价**：
- 读取 Required 检查列表可能需要超出标准 `GITHUB_TOKEN` 的权限（`administration:read`），需在仓库权限配置中明确
- 若 CI 检查长时间挂起，阶段三将无限期等待；需考虑超时处理策略

---

#### 决策五：验收测试（FR-09）与 CI 自动化测试（FR-08）明确分离

**决策**：`tester` Agent 执行的验收测试与 PR CI 自动化测试为两个独立集合，不得相互替代。

**优势**：
- 验收测试由 Agent 逐条模拟执行（可验证业务语义），CI 测试关注构建与单元正确性，两者互补
- 清晰的职责边界防止 tester Agent 错误依赖 CI 结果

**代价**：
- 增加测试总量与执行时间
- **触发时机决策（已确定）**：`testcase-dev` Agent 在 coder Agent 完成代码写入（`artifacts/src/` 非空）且 PR 创建后、tester 启动前触发，与 Section 2.2 "阶段二/三过渡"定位一致；由 `02-coder.yml` 在 coder 步骤成功后以 `workflow_dispatch` 方式触发 `02-testcase-dev.yml`，不得并行于 coder 或提前至架构阶段
