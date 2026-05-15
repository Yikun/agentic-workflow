# Agentic Workflow Installer

用于在仓库中安装、升级、卸载并校验 Agentic Workflow 的 GitHub Actions 工作流模板。该工具将根据架构文档一次性生成 10 个工作流文件，覆盖需求分析、批准门禁、架构设计、编码、测试用例开发、CI 门禁与验收测试阶段。

## 安装（Installation）

### Python 版本要求

- Python >= 3.10

### 安装命令

在仓库根目录执行：

```bash
cd artifacts/src
python -m pip install -U pip
python -m pip install .
```

### 可选依赖

当前版本无第三方运行时依赖，使用 Python 标准库实现。

## 升级（Upgrade）

### 升级代码

```bash
git pull
```

### 重新安装（若版本变化）

```bash
cd artifacts/src
python -m pip install -U .
```

### 重新渲染工作流模板

```bash
agentic-workflow --repo-root ../.. upgrade
```

说明：
- 若使用普通安装（`pip install .`），需要在源码更新后重新执行安装。
- 若改为可编辑安装（`pip install -e .`），源代码改动会立即反映到 CLI 行为，但已落盘的 `.github/workflows/*.yml` 仍需手动执行 `upgrade` 才会更新。

## 卸载（Uninstall）

### 1) 卸载 Python 包

```bash
python -m pip uninstall agentic-workflow-installer
```

### 2) 删除该工具创建的配置文件

默认配置目录：
- `.agentic-workflow/config.json`
- `.agentic-workflow/manifest.json`

可用命令自动删除（默认会删除 manifest，若目录为空也会移除目录）：

```bash
agentic-workflow --repo-root . uninstall
```

若仅想删除工作流并保留配置：

```bash
agentic-workflow --repo-root . uninstall --keep-config
```

### 3) 删除输出目录/文件

本工具主要写入以下目录：
- `.github/workflows/`（10 个阶段工作流文件）

由于 `.github/workflows/` 可能包含其他手工维护文件，通常不建议用单条“递归删除目录”命令清理全部内容。更安全的做法是使用 manifest 精确删除本工具创建的文件（即 `uninstall` 子命令）。

## 快速开始（Quick Start）

```bash
# 1) 安装 CLI
cd artifacts/src
python -m pip install .

# 2) 初始化配置（在仓库根目录执行）
agentic-workflow --repo-root ../.. init-config

# 3) 安装工作流模板
agentic-workflow --repo-root ../.. install

# 4) 校验安装结果
agentic-workflow --repo-root ../.. validate
```

## 配置（Configuration）

### 配置文件位置

- `.agentic-workflow/config.json`

### 配置格式

JSON。

### 配置键说明

- `default_branch`：默认基线分支名，用于模板中的 PR 目标分支。默认值：`main`
- `runner`：GitHub Actions 运行器标签。默认值：`ubuntu-latest`
- `language`：对外输出语言标记。默认值：`zh-CN`

示例：

```json
{
  "default_branch": "main",
  "runner": "ubuntu-latest",
  "language": "zh-CN"
}
```

## CLI 参考（CLI Reference）

命令入口：

```bash
agentic-workflow [--repo-root PATH] <command> [options]
```

全局参数：
- `--repo-root PATH`：仓库根目录，默认 `.`

子命令与参数：
- `init-config`
  - 作用：初始化默认配置文件。
  - 默认行为：若文件已存在则按当前值覆盖保存。
- `install [--dry-run]`
  - 作用：生成并写入全部工作流文件，写入/更新 manifest。
  - `--dry-run`：仅打印将写入的文件，不实际落盘。默认：`false`
- `upgrade [--dry-run]`
  - 作用：基于已安装 manifest 升级模板。
  - `--dry-run`：仅打印将写入的文件，不实际落盘。默认：`false`
- `uninstall [--keep-config] [--dry-run]`
  - 作用：按 manifest 删除已安装工作流并清理 manifest。
  - `--keep-config`：保留 `.agentic-workflow/config.json`。默认：`false`
  - `--dry-run`：仅打印将删除的文件，不实际删除。默认：`false`
- `validate`
  - 作用：检查 manifest 中登记的文件是否存在。
  - 退出码：全部存在返回 `0`；有缺失返回 `2`。
- `list-workflows`
  - 作用：列出该版本预期生成的工作流文件清单。
- `show-config`
  - 作用：打印当前版本、仓库路径与配置值。

## 输出文件（Output Files）

执行 `install` 或 `upgrade` 后，工具会写入：

- `.github/workflows/01-requirements.yml`
  - 阶段一需求文档生成与联动 requirements-qa
- `.github/workflows/01-requirements-qa.yml`
  - 阶段一 QA 与 Issue 下一步提示
- `.github/workflows/02-approve-gate.yml`
  - `/approve` 评论门禁
- `.github/workflows/02-approve-invalidate.yml`
  - 批准失效检测（编辑/删除）
- `.github/workflows/02-architect.yml`
  - 架构阶段
- `.github/workflows/02-architect-qa.yml`
  - 架构 QA 阶段
- `.github/workflows/02-coder.yml`
  - 编码与 PR 创建阶段
- `.github/workflows/02-testcase-dev.yml`
  - 测试用例生成阶段
- `.github/workflows/03-ci-gate.yml`
  - Required CI 门禁
- `.github/workflows/03-tester.yml`
  - 验收测试阶段

以及管理元数据：
- `.agentic-workflow/config.json`：用户配置
- `.agentic-workflow/manifest.json`：安装清单（用于升级/卸载）

阶段三运行时会额外写入：
- `artifacts/04-report.md`：tester 按 `artifacts/03-test-cases.md` 逐条执行后的验收测试报告。

## 已知边界

- `01-requirements.yml`、`01-requirements-qa.yml`、`02-architect.yml`、`02-architect-qa.yml`、`02-coder.yml`、`02-testcase-dev.yml` 中的 Agent 调用步骤仍为占位命令，需按你的执行环境替换。
- `03-ci-gate.yml` 已实现 Required 集合读取（分支保护 + rulesets）与“全部 success 才放行”，若仓库权限不足无法读取 Required 集合，将按门禁未通过处理。
- `03-tester.yml` 已实现逐条读取并执行 `artifacts/03-test-cases.md`，报告结构固定为汇总、逐条结果、失败分析、最终结论。
