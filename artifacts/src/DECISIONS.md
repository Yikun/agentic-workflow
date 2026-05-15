# DECISIONS

## D-01 采用 Python 标准库实现 CLI

- 决策：命令行工具使用 Python 3.10+ 与标准库（`argparse`、`pathlib`、`json`）实现。
- 原因：部署轻量、零第三方依赖、在 GitHub Actions 与本地环境均易运行。
- 取舍：放弃更丰富的第三方 CLI 生态（如 Click/Typer）的高级体验，换取最低安装复杂度。

## D-02 通过模板生成工作流，而非直接在仓库根写死

- 决策：将工作流定义维护在代码模板中，通过 `install/upgrade` 命令渲染到 `.github/workflows/`。
- 原因：可版本化升级、支持 dry-run、可用 manifest 精确回收。
- 取舍：引入了“模板代码 + 生成文件”双层维护成本。

## D-03 使用 manifest 记录安装产物

- 决策：每次安装或升级后写入 `.agentic-workflow/manifest.json`，记录实际写入文件。
- 原因：卸载时只删除工具管理的文件，避免误删仓库中人工维护的其他工作流。
- 取舍：需要保证 manifest 与实际状态一致，手工改动可能造成“部分文件已丢失”的提示。

## D-04 将阶段逻辑拆分为 10 个独立 Workflow 文件

- 决策：按架构文档拆分为 10 个工作流，覆盖阶段与门禁边界。
- 原因：职责清晰、可追溯、符合 FR-12 对“每阶段或子阶段至少一个独立 Workflow 文件”的要求。
- 取舍：跨工作流编排复杂度更高，需要通过 `gh workflow run` 与状态守卫协同。

## D-05 中文优先的文档与交互文本

- 决策：CLI 帮助文本、README、模板提示文案均采用中文优先。
- 原因：满足 FR-11 与项目协作规范，降低人工审阅沟通成本。
- 取舍：多语言支持暂未内建，仅保留 `language` 配置键作为扩展入口。

## D-06 FR-08 采用“Required 集合 + HEAD 状态”双阶段判定

- 决策：在 `03-ci-gate.yml` 中调用 `agentic_workflow.ci_gate`，先从分支保护与 rulesets 读取 Required 集合，再对 PR 当前 HEAD 的 check-runs/statuses 逐项判定，仅全部 `success` 才放行。
- 原因：满足 FR-08 对“Required 作为基准集合”的约束，避免将全部 check-runs 误当 Required。
- 取舍：仓库权限不足时可能无法读取 Required 集合；此时按门禁失败处理，保证安全优先。

## D-07 FR-09 采用“逐条用例执行器 + 固定报告结构”

- 决策：在 `03-tester.yml` 中调用 `agentic_workflow.acceptance`，逐条解析 `artifacts/03-test-cases.md` 并执行自动化校验，始终生成 `artifacts/04-report.md`。
- 原因：满足 FR-09 对“逐条执行、完整报告、与 CI 集合分离”的要求。
- 取舍：未知或新引入的用例 ID 会标记为 `SKIPPED`，需要后续补充对应校验器。
