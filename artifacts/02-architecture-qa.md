### 1. Summary（各严重级别问题汇总）

| 类别 | 数量 |
|------|------|
| Critical（会导致编码者构建错误结构） | 2 |
| Ambiguity（描述不足，编码者将猜测） | 3 |
| Contradiction（两处架构决策冲突，或架构与需求冲突） | 1 |
| Risk（技术上可行但脆弱，需标记缓解建议） | 4 |
| Approved（无问题，明确通过） | 10 |

---

### 2. Critical issues（会导致编码者构建错误结构）

**C-01 · Section 4.3 / `artifacts/state/issue-{issue_number}.json` 作为跨 Workflow 状态存储不可落地**

问题（一句话）：当前设计要求多个独立 Workflow 读写同一工作区文件作为批准与 run_id 状态源，但 GitHub Actions 运行文件系统是按 run 隔离的，未定义持久化机制会导致守卫与失效取消读不到真实状态。

最小修正建议：将状态源改为可跨 run 稳定读取的 GitHub 资源（例如 Issue comment 元数据、Issue label、仓库变量或专用分支文件并显式提交），并在 Section 4.3 固定唯一读写协议。

**C-02 · Section 4.5 / 以 `check-runs` 查询“Required 检查集合”的方法不成立**

问题（一句话）：文档将“Required 检查集合”获取绑定到 Checks API 的 `check-runs` 查询，但该接口不直接返回分支保护中的 required 列表，编码者会误把“全部 check-runs”当作 required 集合而错误放行或错误阻断。

最小修正建议：在 Section 4.5 明确 required 集合来源（分支保护规则/Rulesets）与比对算法（required 集合逐项在 PR 当前 HEAD 上为 success），禁止以“所有 check-runs”替代 required 集合。

---

### 3. Ambiguities（描述不足，编码者将猜测）

**A-01 · Section 2.2 与 Section 5 / architect-qa 阻断后的唯一重触发入口未定义**

问题（一句话）：文档仅写“等待修复后重新触发”，但未规定必须从 `02-architect.yml` 起全链重跑还是允许仅重跑 `02-architect-qa.yml`，会导致不同恢复路径。

最小修正建议：在 Section 2.2 明确阻断后唯一恢复入口与允许的重跑粒度，并在 Issue 通知文案中固定提示该入口。

**A-02 · Section 4.5 / `check_suite.completed` 到目标 PR 的关联与去歧义步骤未写全**

问题（一句话）：文档未明确当一个 SHA 关联多个 PR、或事件来自非目标 PR 时的筛选顺序，编码者将自行补全逻辑并产生误触发差异。

最小修正建议：在 Section 4.5 增加固定过滤流程（按 issue_number 绑定目标 PR → 校验事件 SHA 等于目标 PR 当前 HEAD → 不匹配即退出）。

**A-03 · Section 4.4 × FR-11 / 中文输出要求适用边界未枚举**

问题（一句话）：当前只明确 PR 标题与描述中文，未明确 Issue 评论正文、各阶段 Markdown 产物正文、Workflow 对外提示文案是否同样强制中文。

最小修正建议：新增 FR-11 适用边界清单，逐项标注“强制中文/可内部英文”的对象范围。

---

### 4. Contradictions（两处架构决策冲突，或架构与需求冲突）

**Con-01 · Section 2.3 × Section 4.5 / CI 门禁“轮询”与“事件触发”机制定义冲突**

问题（一句话）：Section 2.3 将 CI 门禁定义为“轮询 PR HEAD Required 检查”，而 Section 4.5 定义为由 `check_suite.completed` 事件触发处理，二者在执行机制上不一致，编码者会实现不同控制流。

最小修正建议：统一为单一门禁机制（纯事件驱动或事件驱动+显式轮询补偿），并在 Section 2.3 与 Section 4.5 使用一致术语。

---

### 5. Risks（技术上可行但脆弱）

**R-01 · Section 4.3 / 批准失效取消依赖权限且存在取消竞态**

问题（一句话）：取消 Workflow run 依赖 `actions:write` 等权限且取消是异步行为，可能在取消生效前已执行后续步骤。

最小修正建议：在 Assumptions 与对应 Workflow `permissions` 明确最小权限，并保留每个阶段二子 Workflow 的首步批准有效性守卫作为兜底。

**R-02 · Section 4.5 / `check_suite.completed` 事件来源宽泛，误推进风险仍高**

问题（一句话）：仓库中非目标分支与非目标 PR 的 check suite 同样会触发事件，若过滤不严会误触发阶段三。

最小修正建议：在门禁中强制“双键校验”（目标 PR 编号 + 目标 PR 当前 HEAD SHA）后才允许推进。

**R-03 · Section 6 决策四 / CI 长时间挂起未固化超时处理策略**

问题（一句话）：文档承认可能无限等待，但未定义超时阈值、通知对象与超时后动作，落地实现将分叉。

最小修正建议：在 Section 4.5 或 Section 6 固化超时规则（阈值、Issue 通知、是否终止或等待人工重触发）。

**R-04 · Section 4.3 / 多 run 并发写同一状态对象存在覆盖风险**

问题（一句话）：同一 Issue 的重试或重复触发可能导致状态被后写覆盖前写，进而让失效判断命中错误 run。

最小修正建议：引入并发控制（按 issue_number 互斥组或版本号 compare-and-set），并记录状态更新时间与来源 run_id 以防误覆盖。

---

### 6. Approved components（无问题，明确通过）

| 组件/章节 | 说明 |
|-----------|------|
| Section 1 系统概述 | 三阶段主线、门禁目标与“无外部服务”约束与需求一致。 |
| Section 2.1 外部交互层（Workflow 清单主体） | 覆盖需求、架构、编码、测试及门禁相关 Workflow，范围完整。 |
| Section 2.2 Agent 执行层（职责划分） | requirements / architect / coder / testcase-dev / tester 职责边界总体清晰。 |
| Section 2.4 产物存储层 | 产物路径与主要读写方映射完整，具备追溯基础。 |
| Section 3 技术选型 | GitHub Actions + Issue/PR + Markdown 的选型与约束匹配。 |
| Section 4.1 入口接口 | `workflow_dispatch + issue_number` 的入口契约明确。 |
| Section 4.2 阶段一接口 | requirements 与 requirements-qa 的输入输出与阻断行为定义清楚。 |
| Section 4.4 阶段二接口（coder） | 代码落盘目录、分支命名与 PR 关联要求明确。 |
| Section 4.6 阶段三接口 | tester 输入结构、输出报告结构、发布方式定义完整。 |
| Section 5 数据流（主干顺序） | requirements → architect → architect-qa → coder → testcase-dev → tester 的顺序一致。 |
