"""Workflow 模板定义。"""

from __future__ import annotations

from .constants import DEFAULT_BRANCH, GENERATED_MARK


def workflow_templates(
    runner: str = "ubuntu-latest",
    default_branch: str = DEFAULT_BRANCH,
) -> dict[str, str]:
    return {
        "00-lint.yml": _lint_template(runner),
        "01-requirements.yml": _requirements_template(runner),
        "01-requirements-qa.yml": _requirements_qa_template(runner),
        "02-approve-gate.yml": _approve_gate_template(runner),
        "02-approve-invalidate.yml": _approve_invalidate_template(runner),
        "02-architect.yml": _architect_template(runner),
        "02-architect-qa.yml": _architect_qa_template(runner),
        "02-coder.yml": _coder_template(runner, default_branch),
        "02-testcase-dev.yml": _testcase_dev_template(runner),
        "03-ci-gate.yml": _ci_gate_template(runner),
        "03-tester.yml": _tester_template(runner),
    }


def _lint_template(runner: str) -> str:
    return f"""{GENERATED_MARK}
name: Lint and Type Check

on:
  pull_request:
          ISSUE_AUTHOR=$(gh issue view "$ISSUE_NO" -R "${{{{ github.repository }}}}" --json author --jq '.author.login')
    branches:
      - main
      - feat/**
      - agentic/**
  workflow_dispatch:
          gh workflow run 02-architect.yml -R "${{{{ github.repository }}}}" -f issue_number="$ISSUE_NO"
permissions:
  contents: read

jobs:
  quality:
    runs-on: {runner}
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: \"3.12\"
      - name: Install check tools
        run: |
          python -m pip install --upgrade pip
          python -m pip install ruff mypy yamllint
      - name: Ruff lint
        run: ruff check .
      - name: Ruff format check
        run: ruff format --check .
      - name: Mypy
        run: mypy artifacts/src
      - name: YAML lint
        run: |
          yamllint -d '{{extends: default, rules: {{document-start: disable, truthy: disable, line-length: {{max: 120}}}}}}' \
            .github/workflows
"""


def _requirements_template(runner: str) -> str:
    return f"""{GENERATED_MARK}
name: Stage 1 - Requirements
on:
  workflow_dispatch:
    inputs:
      issue_number:
        description: \"目标 Issue 编号\"
        required: true
        type: number

permissions:
  contents: write
  actions: write
  issues: write

jobs:
  requirements:
    runs-on: {runner}
    steps:
      - uses: actions/checkout@v4
      - name: 生成需求文档
        run: |
          echo \"请在此步骤调用 requirements Agent\"
          test -f artifacts/01-requirements.md || (echo \"缺少 artifacts/01-requirements.md\" && exit 1)
      - name: 触发 requirements-qa
        env:
          GH_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
        run: |
          gh workflow run 01-requirements-qa.yml -f issue_number=${{{{ inputs.issue_number }}}}
"""


def _requirements_qa_template(runner: str) -> str:
    return f"""{GENERATED_MARK}
name: Stage 1 - Requirements QA
on:
  workflow_dispatch:
    inputs:
      issue_number:
        description: \"目标 Issue 编号\"
        required: true
        type: number

permissions:
  contents: read
  issues: write

jobs:
  requirements_qa:
    runs-on: {runner}
    steps:
      - uses: actions/checkout@v4
      - name: 校验需求文档存在
        run: |
          test -f artifacts/01-requirements.md || (echo \"缺少 artifacts/01-requirements.md\" && exit 1)
      - name: 生成 QA 审查
        run: |
          echo \"请在此步骤调用 requirements-qa Agent\"
      - name: 发布下一步指引评论
        env:
          GH_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
        run: |
          gh issue comment ${{{{ inputs.issue_number }}}} \\
            --body \"需求分析阶段已完成。若认可结果，请由 Issue 作者评论 /approve；若需修改，请直接回复该评论。\"
"""


def _approve_gate_template(runner: str) -> str:
    return f"""{GENERATED_MARK}
name: Stage 2 Gate - Approve
on:
  issue_comment:
    types: [created]

permissions:
  contents: read
  issues: write
  actions: write

jobs:
  approve_gate:
    if: ${{{{ github.event.issue.pull_request == null }}}}
    runs-on: {runner}
    steps:
      - name: 检查 /approve 合法性
        env:
          GH_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
        run: |
          BODY=\"${{{{ github.event.comment.body }}}}\"
          if [ \"$(echo \"$BODY\" | awk '{{gsub(/^ +| +$/,\"\"); print}}')\" != \"/approve\" ]; then
            echo \"评论内容不匹配 /approve，忽略。\"
            exit 0
          fi
          ISSUE_NO=${{{{ github.event.issue.number }}}}
          ISSUE_AUTHOR=$(gh issue view \"$ISSUE_NO\" --json author --jq '.author.login')
          COMMENT_AUTHOR=\"${{{{ github.event.comment.user.login }}}}\"
          if [ \"$ISSUE_AUTHOR\" != \"$COMMENT_AUTHOR\" ]; then
            echo \"仅 Issue 作者可批准。\"
            exit 0
          fi
          gh workflow run 02-architect.yml -f issue_number=\"$ISSUE_NO\"
"""


def _approve_invalidate_template(runner: str) -> str:
    return f"""{GENERATED_MARK}
name: Stage 2 Gate - Approve Invalidate
on:
  issue_comment:
    types: [edited, deleted]

permissions:
  contents: read
  issues: write
  actions: write

jobs:
  invalidate:
    if: ${{{{ github.event.issue.pull_request == null }}}}
    runs-on: {runner}
    steps:
      - name: 处理批准失效
        env:
          GH_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
        run: |
          ISSUE_NO=${{{{ github.event.issue.number }}}}
          gh issue comment \"$ISSUE_NO\" --body \"检测到 /approve 评论被编辑或删除，批准已失效，请重新评论 /approve。\"
"""


def _architect_template(runner: str) -> str:
    return f"""{GENERATED_MARK}
name: Stage 2 - Architect
on:
  workflow_dispatch:
    inputs:
      issue_number:
        description: \"目标 Issue 编号\"
        required: true
        type: number

concurrency:
  group: stage2-${{{{ inputs.issue_number }}}}
  cancel-in-progress: false

permissions:
  contents: write
  issues: write
  actions: write

jobs:
  architect:
    runs-on: {runner}
    steps:
      - uses: actions/checkout@v4
      - name: 守卫检查（批准仍有效）
        run: echo \"请在此实现批准有效性守卫\"
      - name: 生成架构文档
        run: |
          echo \"请在此步骤调用 architect Agent\"
          test -f artifacts/02-architecture.md || (echo \"缺少 artifacts/02-architecture.md\" && exit 1)
      - name: 触发 architect-qa
        env:
          GH_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
        run: |
          gh workflow run 02-architect-qa.yml -f issue_number=${{{{ inputs.issue_number }}}}
"""


def _architect_qa_template(runner: str) -> str:
    return f"""{GENERATED_MARK}
name: Stage 2 - Architect QA
on:
  workflow_dispatch:
    inputs:
      issue_number:
        description: \"目标 Issue 编号\"
        required: true
        type: number

concurrency:
  group: stage2-${{{{ inputs.issue_number }}}}
  cancel-in-progress: false

permissions:
  contents: write
  issues: write

jobs:
  architect_qa:
    runs-on: {runner}
    steps:
      - uses: actions/checkout@v4
      - name: 守卫检查（批准仍有效）
        run: echo \"请在此实现批准有效性守卫\"
      - name: 执行架构 QA
        run: |
          echo \"请在此步骤调用 architect-qa Agent\"
          test -f artifacts/02-architecture-qa.md || (echo \"缺少 artifacts/02-architecture-qa.md\" && exit 1)
      - name: 触发 coder
        env:
          GH_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
        run: |
          gh workflow run 02-coder.yml -f issue_number=${{{{ inputs.issue_number }}}}
"""


def _coder_template(runner: str, default_branch: str) -> str:
    return f"""{GENERATED_MARK}
name: Stage 2 - Coder
on:
  workflow_dispatch:
    inputs:
      issue_number:
        description: \"目标 Issue 编号\"
        required: true
        type: number

concurrency:
  group: stage2-${{{{ inputs.issue_number }}}}
  cancel-in-progress: false

permissions:
  contents: write
  pull-requests: write
  issues: write

jobs:
  coder:
    runs-on: {runner}
    steps:
      - uses: actions/checkout@v4
      - name: 守卫检查（批准仍有效）
        run: echo \"请在此实现批准有效性守卫\"
      - name: 执行编码
        run: |
          echo \"请在此步骤调用 coder Agent\"
          test -d artifacts/src || (echo \"缺少 artifacts/src\" && exit 1)
      - name: 创建 PR
        env:
          GH_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
        run: |
          ISSUE_NO=${{{{ inputs.issue_number }}}}
          BRANCH=agentic/issue-${{{{ inputs.issue_number }}}}
          git checkout -B \"$BRANCH\"
          git add artifacts/src
          git commit -m \"feat: issue-$ISSUE_NO 阶段二代码交付\" || true
          git push --set-upstream origin \"$BRANCH\"
          gh pr create \\
            --base {default_branch} \\
            --head \"$BRANCH\" \\
            --title \"实现 Issue #$ISSUE_NO 的阶段二交付\" \\
            --body \"自动化阶段二产物，Closes #$ISSUE_NO\"
      - name: 触发 testcase-dev
        env:
          GH_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
        run: |
          gh workflow run 02-testcase-dev.yml -R "${{{{ github.repository }}}}" -f issue_number=${{{{ inputs.issue_number }}}}
"""


def _testcase_dev_template(runner: str) -> str:
    return f"""{GENERATED_MARK}
name: Stage 2.5 - Testcase Dev
on:
  workflow_dispatch:
    inputs:
      issue_number:
        description: \"目标 Issue 编号\"
        required: true
        type: number

permissions:
  contents: write
  actions: write
  issues: write

jobs:
  testcase_dev:
    runs-on: {runner}
    steps:
      - uses: actions/checkout@v4
      - name: 生成验收用例
        run: |
          echo \"请在此步骤调用 testcase-dev Agent\"
          test -f artifacts/03-test-cases.md || (echo \"缺少 artifacts/03-test-cases.md\" && exit 1)
      - name: 触发 tester
        env:
          GH_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
        run: |
          gh issue comment \"${{{{ inputs.issue_number }}}}\" -R \"${{{{ github.repository }}}}\" --body \"验收测试用例已生成，自动进入第三阶段测试。\"
          gh workflow run 03-tester.yml -R \"${{{{ github.repository }}}}\" -f issue_number=\"${{{{ inputs.issue_number }}}}\"
"""


def _ci_gate_template(runner: str) -> str:
    return f"""{GENERATED_MARK}
name: Stage 3 Gate - CI
on:
  check_suite:
    types: [completed]

permissions:
  contents: read
  actions: write
  issues: write
  checks: read

jobs:
  ci_gate:
    runs-on: {runner}
    steps:
      - uses: actions/checkout@v4
      - name: 校验 Required CI 检查是否全部成功
        id: gate
        env:
          GH_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
        run: |
          python -m agentic_workflow.ci_gate \\
            --event-path \"$GITHUB_EVENT_PATH\" \\
            --repo \"${{{{ github.repository }}}}\" \\
            --output \"$GITHUB_OUTPUT\"
      - name: 触发 tester
        if: ${{{{ steps.gate.outputs.pass == 'true' }}}}
        env:
          GH_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
        run: |
          ISSUE_NO=\"${{{{ steps.gate.outputs.issue_number }}}}\"
          gh issue comment "$ISSUE_NO" -R "${{{{ github.repository }}}}" --body "PR Required CI 检查已全部通过，自动进入第三阶段测试。"
          gh workflow run 03-tester.yml -R "${{{{ github.repository }}}}" -f issue_number="$ISSUE_NO"
      - name: 记录门禁未通过原因
        if: ${{{{ steps.gate.outputs.pass != 'true' }}}}
        run: |
          echo \"CI 门禁未通过：${{{{ steps.gate.outputs.reason }}}}\"
"""


def _tester_template(runner: str) -> str:
    return f"""{GENERATED_MARK}
name: Stage 3 - Tester
on:
  workflow_dispatch:
    inputs:
      issue_number:
        description: \"目标 Issue 编号\"
        required: true
        type: number

permissions:
  contents: write
  issues: write

jobs:
  tester:
    runs-on: {runner}
    steps:
      - uses: actions/checkout@v4
      - name: 执行验收测试
        id: acceptance
        continue-on-error: true
        run: |
          python -m agentic_workflow.acceptance \\
            --repo-root . \\
            --test-cases artifacts/03-test-cases.md \\
            --source-dir artifacts/src \\
            --report artifacts/04-report.md \\
            --output \"$GITHUB_OUTPUT\"
      - name: 发布测试结论
        env:
          GH_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
        run: |
          RESULT=\"${{{{ steps.acceptance.outputs.final_result }}}}\"
          gh issue comment ${{{{ inputs.issue_number }}}} --body \"阶段三测试已完成，结论：$RESULT。请查看 artifacts/04-report.md。\"
      - name: 若验收失败则标记工作流失败
        if: ${{{{ steps.acceptance.outputs.final_result != 'PASS' }}}}
        run: |
          echo \"验收测试结论为 FAIL。\"
          exit 1
"""
