# Agentic Workflow 验收测试用例

## 范围说明
- 测试对象：基于 `artifacts/src/` 交付的安装器与工作流模板。
- 测试方式：静态检查 + 命令触发后的产物/文本校验 + 逻辑推演。
- 约束：本文件仅定义用例，不执行测试。

---

### TC-01 从 Issue 读取流程输入
- Requirement: FR-01
- Preconditions:
	- 仓库已安装工作流模板。
	- 存在编号为 `123` 的 GitHub Issue，且包含原始需求描述。
- Steps:
	1. 触发 `01-requirements.yml`，传入 `issue_number=123`。
	2. 检查工作流入口参数是否要求 `issue_number` 且类型为 number。
	3. 检查需求生成步骤是否围绕该 Issue 编号执行。
- Expected result:
	- 流程可基于指定 Issue 编号启动，并将该 Issue 作为需求来源。
- Type: 功能

### TC-02 需求阶段双 Agent 产出与校验
- Requirement: FR-02
- Preconditions:
	- 已存在 `artifacts/01-requirements.md`。
- Steps:
	1. 检查 `01-requirements.yml` 中需求阶段步骤。
	2. 检查 `01-requirements.yml` 是否触发 `01-requirements-qa.yml`。
	3. 检查 `01-requirements-qa.yml` 是否校验 `artifacts/01-requirements.md` 存在。
- Expected result:
	- requirements 与 requirements-qa 两类 Agent 均有对应阶段与职责。
	- 需求文档初稿与 QA 校验链路完整。
- Type: 功能

### TC-03 需求结果评论包含下一步指引
- Requirement: FR-03
- Preconditions:
	- `01-requirements-qa.yml` 可触发执行。
- Steps:
	1. 检查 `01-requirements-qa.yml` 的 Issue 评论发布步骤。
	2. 核对评论文案是否同时包含“认可则 /approve”和“不认可则回复修改意见”。
- Expected result:
	- 需求阶段结果发布到原 Issue 评论。
	- 评论中明确给出批准与修改两条下一步路径。
- Type: 功能

### TC-04 批准门禁：合法 /approve 可进入第二阶段
- Requirement: FR-04
- Preconditions:
	- Issue 作者为 `alice`。
	- 出现一条新评论，正文为 `/approve`，作者为 `alice`，且评论未编辑未删除。
- Steps:
	1. 触发 `02-approve-gate.yml` 的 `issue_comment.created`。
	2. 检查正文去空白后的精确匹配逻辑。
	3. 检查评论作者与 Issue 作者一致性校验。
	4. 检查是否触发 `02-architect.yml`。
- Expected result:
	- 仅当评论满足批准条件时，触发第二阶段架构流程。
- Type: 功能

### TC-05 边界：/approve 前后空白字符
- Requirement: FR-04
- Preconditions:
	- Issue 作者发布评论正文为 `  /approve  `。
- Steps:
	1. 触发 `02-approve-gate.yml`。
	2. 观察正文 trim 后匹配结果。
- Expected result:
	- 去除首尾空白后仍精确等于 `/approve`，可视为有效批准。
- Type: 边界

### TC-06 边界：混合文本评论不构成批准
- Requirement: FR-04
- Preconditions:
	- Issue 作者发布评论正文为 `/approve 请继续`。
- Steps:
	1. 触发 `02-approve-gate.yml`。
	2. 检查匹配逻辑与后续是否触发 `02-architect.yml`。
- Expected result:
	- 因不满足“仅包含 /approve”要求，不触发第二阶段。
- Type: 边界

### TC-07 边界：非 Issue 作者评论 /approve
- Requirement: FR-04
- Preconditions:
	- Issue 作者为 `alice`。
	- 用户 `bob` 发表评论 `/approve`。
- Steps:
	1. 触发 `02-approve-gate.yml`。
	2. 检查作者校验分支。
- Expected result:
	- 非 Issue 作者批准无效，不触发第二阶段。
- Type: 边界

### TC-08 批准失效：编辑或删除后立即失效
- Requirement: FR-04
- Preconditions:
	- 曾存在有效 `/approve` 评论。
- Steps:
	1. 触发 `02-approve-invalidate.yml` 的 `issue_comment.edited`。
	2. 触发 `02-approve-invalidate.yml` 的 `issue_comment.deleted`。
	3. 检查是否向 Issue 发布“批准失效，需重新 /approve”评论。
- Expected result:
	- 编辑或删除均会触发失效提示，批准状态不可继续沿用。
- Type: 功能

### TC-09 第二阶段产出架构文档
- Requirement: FR-05
- Preconditions:
	- 第二阶段已获准进入。
- Steps:
	1. 触发 `02-architect.yml`。
	2. 检查是否校验 `artifacts/02-architecture.md` 的存在。
	3. 检查完成后是否触发 `02-architect-qa.yml`。
- Expected result:
	- 架构文档作为阶段必需产物被生成并进入 QA 链路。
- Type: 功能

### TC-10 第二阶段代码产出目录约束
- Requirement: FR-06
- Preconditions:
	- 已进入 `02-coder.yml`。
- Steps:
	1. 检查 `02-coder.yml` 的编码产出校验。
	2. 核对是否要求 `artifacts/src/` 目录存在。
- Expected result:
	- 阶段二代码交付以 `artifacts/src/` 为必需存储位置。
- Type: 功能

### TC-11 第二阶段完成后创建 PR
- Requirement: FR-07
- Preconditions:
	- `artifacts/src/` 下存在待提交变更。
- Steps:
	1. 检查 `02-coder.yml` 中分支创建、提交、推送、`gh pr create` 步骤。
	2. 核对 PR 标题和描述是否关联目标 Issue（`Closes #issue_number`）。
- Expected result:
	- 第二阶段结束后创建 PR 提交代码变更。
- Type: 功能

### TC-12 CI 门禁严格依赖 Required 检查全成功
- Requirement: FR-08
- Preconditions:
	- 存在目标 PR 与对应 HEAD 提交。
	- 触发 `03-ci-gate.yml` 的 `check_suite.completed` 事件。
- Steps:
	1. 构造场景 A：所有 Required 检查为 success。
	2. 构造场景 B：至少一个 Required 检查为 failure/cancelled/timed_out/pending/missing。
	3. 构造场景 C：Required 集合为空。
	4. 验证仅场景 A 可继续触发 `03-tester.yml`。
- Expected result:
	- 仅“全部 Required=success”可进入第三阶段。
	- 失败、取消、超时、待运行、缺失、空集合均不得放行。
- Type: 功能

### TC-13 第三阶段逐条执行测试并生成报告
- Requirement: FR-09
- Preconditions:
	- `artifacts/03-test-cases.md` 已定义多条用例。
	- `artifacts/src/` 存在被测交付代码。
- Steps:
	1. 触发 `03-tester.yml`。
	2. 检查 tester 阶段是否按用例逐条执行（可调用代码、检查输出或逻辑推演）。
	3. 检查 `artifacts/04-report.md` 是否包含：汇总表、逐条结果、失败分析、最终 PASS/FAIL。
	4. 检查 CI 自动化测试结果与验收测试结果是否分开记录，不互相替代。
- Expected result:
	- 第三阶段输出完整测试报告，且与 FR-08 的 CI 检查集合保持独立。
- Type: 功能

### TC-14 阶段结果可追踪
- Requirement: FR-10
- Preconditions:
	- 三阶段流程至少运行一轮。
- Steps:
	1. 检查阶段一产物（需求文档）与 Issue 评论关联。
	2. 检查阶段二产物（架构文档、代码、PR）关联。
	3. 检查阶段三产物（测试报告）与 Issue 或仓库文件关联。
- Expected result:
	- 各阶段均有明确产物与可追踪位置，用户可在 Issue/PR 中追踪状态。
- Type: 功能

### TC-15 对外沟通与文档语言为中文
- Requirement: FR-11
- Preconditions:
	- 已生成 README、工作流提示文案、Issue 评论文案等对外内容。
- Steps:
	1. 抽查 `README.md`、模板中 `gh issue comment` 文案、阶段文档标题与正文。
	2. 检查是否使用中文表达，术语一致。
- Expected result:
	- 对外沟通内容与产出文档默认使用中文。
- Type: 功能

### TC-16 工作流文件布局与数量
- Requirement: FR-12
- Preconditions:
	- 安装器可执行 `install` 或 `list-workflows`。
- Steps:
	1. 检查模板输出目标目录是否为 `.github/workflows/`。
	2. 检查文件格式是否为 YAML（`.yml`）。
	3. 核对是否覆盖需求分析、架构设计、编码开发、测试执行与门禁子阶段。
	4. 核对独立工作流文件数量不少于阶段/子阶段要求（当前实现为 10 个）。
- Expected result:
	- 自动化触发逻辑以独立 YAML Workflow 文件存储在 `.github/workflows/`。
	- 阶段与子阶段覆盖完整。
- Type: 功能

---

## 覆盖汇总
- 覆盖需求：FR-01, FR-02, FR-03, FR-04, FR-05, FR-06, FR-07, FR-08, FR-09, FR-10, FR-11, FR-12
- 用例总数：16
- 边界用例：4（TC-05, TC-06, TC-07, TC-12 中场景 C）
