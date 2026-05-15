# Requirements QA Review — 01-requirements.md

审查日期：2026-05-15
审查人：Requirements QA Agent

---

### 1. Summary（各严重级别问题汇总）

| 类别 | 数量 |
|------|------|
| Critical（会导致编码者实现错误） | 0 |
| Ambiguity（描述不足，编码者将猜测） | 9 |
| Contradiction（两条需求互相冲突） | 0 |
| Feasibility Concern（技术上存疑，标记但不解决） | 2 |
| Approved（无问题，明确通过） | 17 |

与上一版比较：上一版 C-01（FR-06 × FR-09 代码输出路径冲突）已在当前版本中通过 FR-06 明确规定「所有代码文件须存储至当前仓库的 `artifacts/src/` 目录下」完全解决，本版 Critical Issues 归零。9 条 Ambiguity 及 2 条 Feasibility Concern 在本版中均未被修正，维持原判定。

---

### 2. Critical Issues（会导致编码者实现错误的问题）

无。当前版本未发现会导致编码者实现错误的关键性缺陷。

---

### 3. Ambiguities（描述不足，编码者将猜测）

**A-01 · FR-01**
问题：「指定 GitHub Issue」的传入机制完全未定义，编码者不知道 Issue 标识符以何种形式进入系统（workflow_dispatch input 字段？环境变量？Issue URL？Issue Number？）。
最小修正：明确传入方式，例如：「通过 workflow_dispatch 触发时的 `issue_number` input 字段（整数类型）传入」。

**A-02 · FR-02**
问题：requirements-qa Agent 发现阻断性问题后，系统响应路径未定义——不知道应终止当次流程并通知用户修订后重新触发，还是携带 QA 报告继续进入 FR-04 等待态，或执行其他路径。
最小修正：补充阻断性问题时的系统行为，例如：「发布 QA 报告至 Issue 评论并以非零退出码终止 Workflow，等待人工修订后重新触发」。

**A-03 · FR-03**
问题：「需求分析阶段结果」发布到 Issue 评论的具体内容范围未定义，编码者不知道应发布需求文档全文、QA 审查报告摘要、还是两者的合并摘要，以及是否附加 artifacts/ 文件链接。
最小修正：枚举评论中包含的具体产物，例如：「需求文档全文 + QA 审查报告摘要 + artifacts 文件链接」。

**A-04 · FR-05**
问题：架构设计文档的输出路径（文件名）及必要章节结构未定义，编码者将随意选择存储位置和文档格式。
最小修正：声明输出路径（例如 `artifacts/02-architecture.md`）并列举必要章节（例如：总体架构图、模块职责、阶段间数据流、Workflow 文件清单）。

**A-05 · FR-06**
问题：代码变更所在的 feature branch 命名规范未定义，编码者无法确定分支名；同名分支已存在时应删除重建、追加提交还是报错退出的处理策略亦未定义。
最小修正：规定命名规则（例如 `agentic/issue-{issue_number}`）并明确同名分支冲突处理策略。

**A-06 · FR-07**
问题：（1）PR 的目标基础分支（base branch）未指定，编码者将随意选择；（2）「第二阶段完成」的判定条件未定义——代码写入文件即完成，还是需通过本地 lint/格式/构建校验后才可创建 PR，两种假设导致截然不同的实现。
最小修正：（1）指定 PR base branch（例如 `main`）；（2）定义「第二阶段完成」的可验证判定条件。

**A-07 · FR-09 × ASS-05**
问题：（1）`artifacts/03-test-cases.md` 的条目格式/结构未定义，testcase-dev Agent（写入端）与 tester Agent（读取端）将各自实现不兼容的格式；（2）ASS-05 措辞为「已提供或可提供」（暗示外部输入），与 `agents/testcase-dev/` 的存在相矛盾——testcase-dev 在自动化流程中的触发时机与所处阶段在任何 FR 中均无定义，编码者无法实现其 Workflow 触发逻辑。
最小修正：（1）在 FR-09 或独立 FR 中定义 03-test-cases.md 的条目结构（例如：ID / 描述 / 前置条件 / 预期输出）；（2）明确 testcase-dev 是否为自动化流程的一部分，若是，则补充其触发阶段及输出规范。

**A-08 · FR-11**
问题：「对外沟通内容与产出文档使用中文」的适用范围不明确——commit message、PR 标题/描述、代码注释、branch 名称、YAML 文件内容是否须使用中文未作说明，编码者将各自随意决定。
最小修正：明确「中文」要求的适用边界，例如：「适用于 Issue/PR 评论文本及 Markdown 产出文档正文；不适用于 commit message、branch 名称、代码注释及 YAML key/value」，或反之明确全部适用。

**A-09 · FR-12**
问题：「每个阶段或子阶段至少对应一个独立的 Workflow 文件」中「子阶段」未枚举定义——需求描述三个顶层阶段，但未说明 requirements/requirements-qa/architect/coder/tester/testcase-dev 各是否为独立子阶段，编码者无法确定最少需要创建几个 Workflow 文件及其职责边界。
最小修正：枚举所有子阶段名称（例如：requirements、requirements-qa、architect、coder、testcase-dev、tester）并给出 Workflow 文件最小数量，或直接列出文件名清单。

---

### 4. Contradictions（两条需求互相冲突）

无。当前版本未发现需求间相互冲突的条目。

---

### 5. Feasibility Concerns（技术上存疑，标记但不解决）

**F-01 · FR-04**
问题：「若该批准评论被编辑或删除，批准立即失效」要求对评论变更进行实时感知；FR-12 规定使用 GitHub Actions 实现——GitHub Actions 为离散事件触发模型，第二阶段执行期间无法持续监听 Issue 评论的编辑/删除事件，「立即」语义在技术上无法保证。
标记：建议架构师明确「立即失效」的实现边界——是「在下次系统检查时判定无效」（延迟检测，GitHub Actions 可实现），还是「中断当前阶段执行」（需额外 Webhook + 实时监听基础设施）。

**F-02 · FR-08**
问题：读取 PR 的「Required」状态检查列表（branch protection rules）需要 GitHub API 的 `administration:read` 或等效权限；标准 `GITHUB_TOKEN` 在非 Owner/Admin 仓库中通常不具备此权限，可能需要具有该权限的 PAT 或 GitHub App Token，但 ASS-01 仅泛称「必要的 GitHub 权限配置」，未验证是否包含此具体权限。
标记：建议在 ASS-01 中显式列出所需权限范围（`repo`、`checks:read`、`administration:read` 等），或验证 `GITHUB_TOKEN` 在目标仓库中可读取 branch protection 配置。

---

### 6. Approved Requirements（无问题，明确通过）

| FR/NFR/ASS/OOS | 说明 |
|----------------|------|
| **FR-01** | 读取 Issue 作为输入的意图清晰；传入机制歧义已在 A-01 单独标记，不影响通过。 |
| **FR-04** | 审批核心逻辑完整无歧义：精确匹配、大小写敏感、多条取最早、仅限原作者、编辑/删除失效；实现边界已在 F-01 标记，不影响通过。 |
| **FR-06（路径部分）** | 「所有代码文件须存储至当前仓库的 `artifacts/src/` 目录下」已明确，FR-06 × FR-09 路径冲突（前版 C-01）完全解决；branch 命名歧义已在 A-05 单独标记。 |
| **FR-08** | CI 通过/阻断/空集合三种条件定义清晰完整；所需 API 权限可行性已在 F-02 标记，不影响通过。 |
| **FR-09（执行机制部分）** | 执行主体（tester Agent）、来源文件（artifacts/03-test-cases.md）、待测目标（artifacts/src/）、验证方式（调用/检查输出/逻辑推演）、报告路径（artifacts/04-report.md）、报告结构（汇总表/逐条说明/失败分析/结论）均已明确；与 FR-08 互不替代的声明清晰。格式与触发歧义已在 A-07 单独标记。 |
| **FR-10** | 各阶段产出与 Issue/PR 追踪路径清晰，与 FR-03、FR-07 一致，无歧义。 |
| **NFR-01** | 可追溯性要求清晰，与 FR-03、FR-07、FR-10 配合可验证。 |
| **NFR-02** | 阶段门禁可靠性要求清晰，与 FR-04、FR-08 一致。 |
| **NFR-03** | 结构一致性要求明确且可验证。 |
| **NFR-04** | 可读性要求明确。 |
| **NFR-05** | 自动化连续性描述可量化（除 FR-04 明确人工审批外，不要求额外手动操作），无歧义。 |
| **ASS-01** | 合理；需配合 F-02 核查 `administration:read` 权限是否已包含。 |
| **ASS-02** | 合理且可验证。 |
| **ASS-03** | 合理且可验证。 |
| **ASS-04** | 合理，与 FR-04 一致。 |
| **ASS-05** | 合理；与 A-07 的 testcase-dev 歧义共存，建议联动修正。 |
| **OOS-01 ~ OOS-04** | 排除项表述清晰，无歧义。 |
