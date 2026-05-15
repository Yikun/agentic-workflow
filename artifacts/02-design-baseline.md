# 开发前设计基线（Baseline）

基线编号：DESIGN-BASELINE-2026-05-15-01
基线日期：2026-05-15
状态：已提交（开发前冻结输入）

## 1. 基线范围

- 需求基线：`artifacts/01-requirements.md`
- 架构基线：`artifacts/02-architecture.md`
- 需求审查快照：`artifacts/01-requirements-qa.md`
- 架构审查快照：`artifacts/02-architecture-qa.md`

## 2. 当前质量快照

- Requirements QA：Critical=0，Contradictions=0
- Architecture QA：Critical=2，Contradictions=1

说明：本基线用于“开发前版本冻结与评审对齐”。架构侧仍有阻断项，编码阶段应在阻断项清零后启动。

## 3. 阶段一评论提醒（已纳入基线）

阶段一输出到 Issue 的评论必须包含明确下一步引导：

- 认可结果：请评论 `/approve`
- 需要修改：请直接回复评论提出修改意见

## 4. 变更控制规则

- 任何对需求或架构的修改，均应先更新对应 QA 文档并记录影响范围。
- 未更新本基线前，不得将“新设计决策”直接视为开发输入。
- 开发输入以本基线列出的文件为准；若文件发生实质变化，需提交新基线版本（例如 `...-02`）。

## 5. 开发准入条件

- 必选：`artifacts/02-architecture-qa.md` 中 Critical=0 且 Contradictions=0
- 必选：需求与架构中的阶段门禁定义保持一致（`/approve`、CI Required 检查规则）
- 建议：对剩余 Ambiguity 给出最小实现约束，减少实现分叉
