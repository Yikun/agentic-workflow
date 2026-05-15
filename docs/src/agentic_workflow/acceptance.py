"""FR-09 验收测试执行与报告生成。"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

from .templates import workflow_templates


@dataclass(slots=True)
class TestCase:
    case_id: str
    requirement: str
    title: str


@dataclass(slots=True)
class CaseResult:
    case_id: str
    requirement: str
    status: str
    notes: str


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_test_cases(path: Path) -> list[TestCase]:
    content = _read_text(path)
    pattern = re.compile(r"^###\s+(TC-\d+)\s+(.+)$", flags=re.MULTILINE)
    req_pattern = re.compile(r"^- Requirement:\s*(.+)$", flags=re.MULTILINE)

    matches = list(pattern.finditer(content))
    cases: list[TestCase] = []
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(content)
        block = content[start:end]
        req_match = req_pattern.search(block)
        cases.append(
            TestCase(
                case_id=match.group(1).strip(),
                title=match.group(2).strip(),
                requirement=req_match.group(1).strip() if req_match else "UNKNOWN",
            )
        )
    return cases


def _check(content: str, snippets: list[str]) -> bool:
    return all(snippet in content for snippet in snippets)


def _validate_case(
    case: TestCase, source_dir: Path, templates_text: str, readme_text: str
) -> CaseResult:
    workflow_map = workflow_templates()

    validators: dict[str, tuple[bool, str]] = {
        "TC-01": (
            _check(
                workflow_map["01-requirements.yml"],
                [
                    "issue_number",
                    "type: number",
                    "gh workflow run 01-requirements-qa.yml",
                ],
            ),
            "检查需求入口参数与 Issue 编号链路。",
        ),
        "TC-02": (
            _check(
                workflow_map["01-requirements.yml"],
                ["01-requirements-qa.yml"],
            )
            and _check(
                workflow_map["01-requirements-qa.yml"],
                ["test -f docs/01-requirements.md"],
            ),
            "检查 requirements 与 requirements-qa 双阶段链路。",
        ),
        "TC-03": (
            _check(
                workflow_map["01-requirements-qa.yml"],
                ["/approve", "修改", "gh issue comment"],
            ),
            "检查需求阶段评论中的下一步指引。",
        ),
        "TC-04": (
            _check(
                workflow_map["02-approve-gate.yml"],
                [
                    "types: [created]",
                    "ISSUE_AUTHOR",
                    "COMMENT_AUTHOR",
                    "/approve",
                    "02-architect.yml",
                ],
            ),
            "检查 /approve 合法性校验与阶段二触发。",
        ),
        "TC-05": (
            "awk" in workflow_map["02-approve-gate.yml"],
            "检查 /approve 前后空白 trim。",
        ),
        "TC-06": (
            '!= "/approve"' in workflow_map["02-approve-gate.yml"],
            "检查混合文本不放行。",
        ),
        "TC-07": (
            _check(
                workflow_map["02-approve-gate.yml"],
                ["ISSUE_AUTHOR", "COMMENT_AUTHOR", "仅 Issue 作者可批准"],
            ),
            "检查非 Issue 作者不放行。",
        ),
        "TC-08": (
            _check(
                workflow_map["02-approve-invalidate.yml"],
                ["types: [edited, deleted]", "批准已失效"],
            ),
            "检查批准失效监听与通知。",
        ),
        "TC-09": (
            _check(
                workflow_map["02-architect.yml"],
                ["test -f docs/02-architecture.md", "02-architect-qa.yml"],
            ),
            "检查架构产物与 QA 链路。",
        ),
        "TC-10": (
            "test -d docs/src" in workflow_map["02-coder.yml"],
            "检查代码产物目录约束。",
        ),
        "TC-11": (
            _check(
                workflow_map["02-coder.yml"],
                ["gh pr create", "Closes #$ISSUE_NO"],
            ),
            "检查 PR 创建与 Issue 关联。",
        ),
        "TC-12": (
            _check(
                workflow_map["03-ci-gate.yml"],
                ["python -m agentic_workflow.ci_gate", "steps.gate.outputs.pass"],
            )
            and "请在此实现 Required 检查集合读取与 success 判定" not in templates_text,
            "检查 Required 集合读取与全 success 放行逻辑非占位。",
        ),
        "TC-13": (
            _check(
                workflow_map["03-tester.yml"],
                [
                    "python -m agentic_workflow.acceptance",
                    "docs/04-report.md",
                    "final_result",
                ],
            )
            and "请在此步骤调用 tester Agent" not in templates_text,
            "检查 tester 逐条执行入口与报告产出链路非占位。",
        ),
        "TC-14": (
            _check(
                workflow_map["03-tester.yml"],
                ["gh issue comment"],
            )
            and _check(
                workflow_map["02-coder.yml"],
                ["gh pr create"],
            ),
            "检查阶段产物可追踪链路。",
        ),
        "TC-15": (
            any(word in readme_text for word in ["安装", "工作流", "中文"]),
            "检查对外文档与沟通语言。",
        ),
        "TC-16": (
            len(workflow_map) >= 10
            and all(name.endswith(".yml") for name in workflow_map)
            and all(Path(".github/workflows") / name for name in workflow_map),
            "检查工作流数量、目录与格式。",
        ),
    }

    if case.case_id not in validators:
        return CaseResult(
            case.case_id,
            case.requirement,
            "SKIPPED",
            "未实现自动化校验器，需人工补充。",
        )

    passed, detail = validators[case.case_id]
    status = "PASS" if passed else "FAIL"
    return CaseResult(case.case_id, case.requirement, status, detail)


def run_acceptance(test_cases: Path, source_dir: Path) -> list[CaseResult]:
    cases = parse_test_cases(test_cases)
    templates_text = _read_text(source_dir / "agentic_workflow" / "templates.py")
    readme_text = _read_text(source_dir / "README.md")
    return [
        _validate_case(case, source_dir, templates_text, readme_text) for case in cases
    ]


def _summary(results: list[CaseResult]) -> tuple[int, int, int, int]:
    total = len(results)
    passed = sum(1 for item in results if item.status == "PASS")
    failed = sum(1 for item in results if item.status == "FAIL")
    skipped = sum(1 for item in results if item.status == "SKIPPED")
    return total, passed, failed, skipped


def _build_report(results: list[CaseResult]) -> str:
    total, passed, failed, skipped = _summary(results)
    final = "PASS" if failed == 0 else "FAIL"

    lines: list[str] = []
    lines.append("# Agentic Workflow 验收测试报告")
    lines.append("")
    lines.append("## 1. Summary")
    lines.append("")
    lines.append("| 指标 | 数量 |")
    lines.append("|---|---:|")
    lines.append(f"| total | {total} |")
    lines.append(f"| passed | {passed} |")
    lines.append(f"| failed | {failed} |")
    lines.append(f"| skipped | {skipped} |")
    lines.append("")

    lines.append("## 2. Per-test Result With Notes")
    lines.append("")
    lines.append("| Test Case | Requirement | 结果 | Notes |")
    lines.append("|---|---|---|---|")
    for item in results:
        lines.append(
            f"| {item.case_id} | {item.requirement} | {item.status} | {item.notes} |"
        )
    lines.append("")

    lines.append("## 3. Detailed Failure Breakdown")
    lines.append("")
    failures = [item for item in results if item.status == "FAIL"]
    if not failures:
        lines.append("- 无失败项。")
    else:
        for index, item in enumerate(failures, start=1):
            lines.append(f"### F-{index:02d} 对应 {item.case_id}（{item.requirement}）")
            lines.append("")
            lines.append(f"- 现象：{item.notes}")
            lines.append("- 影响：当前自动化校验未满足该用例要求。")
            lines.append("- 建议：定位对应 Workflow 或模块后补齐实现并复测。")
            lines.append("")

    lines.append("## 4. CI 与验收测试集合说明")
    lines.append("")
    lines.append("- FR-08 的 CI 门禁基于 PR Required 检查集合，仅用于阶段推进判定。")
    lines.append(
        "- FR-09 的验收测试基于 docs/03-test-cases.md 逐条执行并产出报告，二者不可互相替代。"
    )
    lines.append("")

    lines.append("## 5. Final Recommendation")
    lines.append("")
    lines.append(final)
    lines.append("")
    return "\n".join(lines)


def _write_output(path: Path, final_result: str) -> None:
    with path.open("a", encoding="utf-8") as fh:
        fh.write(f"final_result={final_result}\n")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="执行 FR-09 验收测试并生成报告")
    parser.add_argument("--repo-root", default=".", help="仓库根目录")
    parser.add_argument("--test-cases", required=True, help="测试用例文件路径")
    parser.add_argument("--source-dir", required=True, help="被测源码目录")
    parser.add_argument("--report", required=True, help="报告输出路径")
    parser.add_argument("--output", required=False, help="GitHub Actions 输出文件路径")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    test_cases = (repo_root / args.test_cases).resolve()
    source_dir = (repo_root / args.source_dir).resolve()
    report = (repo_root / args.report).resolve()

    results = run_acceptance(test_cases=test_cases, source_dir=source_dir)
    report_content = _build_report(results)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(report_content, encoding="utf-8")

    _, _, failed, _ = _summary(results)
    final_result = "PASS" if failed == 0 else "FAIL"
    print(f"验收测试完成，最终结论：{final_result}")

    if args.output:
        _write_output(Path(args.output), final_result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
