"""FR-08 CI 门禁：按 Required 集合校验 PR HEAD 状态。"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


class CiGateError(RuntimeError):
    """CI 门禁执行错误。"""


@dataclass(slots=True)
class GateResult:
    passed: bool
    reason: str
    issue_number: str = ""


def _run_gh_api(path: str, *, method: str = "GET", hostname: str | None = None) -> dict:
    cmd = ["gh", "api", "-X", method, path]
    if hostname:
        cmd.extend(["--hostname", hostname])

    proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if proc.returncode != 0:
        raise CiGateError(proc.stderr.strip() or f"gh api 调用失败: {path}")

    output = proc.stdout.strip()
    if not output:
        return {}
    return json.loads(output)


def _load_event(path: Path) -> dict:
    if not path.exists():
        raise CiGateError(f"事件文件不存在: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_repo(repo: str) -> tuple[str, str]:
    parts = repo.split("/", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise CiGateError(f"仓库格式不正确: {repo}")
    return parts[0], parts[1]


def _required_from_branch_protection(
    owner: str, repo: str, base_branch: str
) -> set[str]:
    path = f"/repos/{owner}/{repo}/branches/{base_branch}/protection/required_status_checks"
    data = _run_gh_api(path)
    contexts = data.get("contexts", [])
    checks = data.get("checks", [])
    names = {str(name) for name in contexts if str(name).strip()}
    for item in checks:
        name = str(item.get("context", "")).strip()
        if name:
            names.add(name)
    return names


def _required_from_rulesets(owner: str, repo: str, base_branch: str) -> set[str]:
    path = f"/repos/{owner}/{repo}/rulesets"
    rulesets = _run_gh_api(path)
    required: set[str] = set()

    if not isinstance(rulesets, list):
        return required

    for ruleset in rulesets:
        enforcement = str(ruleset.get("enforcement", ""))
        if enforcement != "active":
            continue

        conditions = ruleset.get("conditions", {})
        ref_name = (
            conditions.get("ref_name", {}) if isinstance(conditions, dict) else {}
        )
        include = ref_name.get("include", []) if isinstance(ref_name, dict) else []
        if not _ruleset_applies_to_branch(base_branch, include):
            continue

        for rule in ruleset.get("rules", []):
            if str(rule.get("type", "")) != "required_status_checks":
                continue
            parameters = rule.get("parameters", {})
            for req in parameters.get("required_status_checks", []):
                name = str(req.get("context", "")).strip()
                if name:
                    required.add(name)

    return required


def _ruleset_applies_to_branch(base_branch: str, include: list[str]) -> bool:
    if not include:
        return True

    refs = [str(value).replace("refs/heads/", "") for value in include]
    for ref in refs:
        if ref == "~DEFAULT_BRANCH":
            return True
        if "*" in ref:
            regex = "^" + re.escape(ref).replace("\\*", ".*") + "$"
            if re.match(regex, base_branch):
                return True
        if ref == base_branch:
            return True
    return False


def _head_states(owner: str, repo: str, head_sha: str) -> dict[str, str]:
    checks_path = f"/repos/{owner}/{repo}/commits/{head_sha}/check-runs"
    statuses_path = f"/repos/{owner}/{repo}/commits/{head_sha}/statuses"

    states: dict[str, str] = {}

    checks = _run_gh_api(checks_path)
    for run in checks.get("check_runs", []):
        name = str(run.get("name", "")).strip()
        status = str(run.get("status", "")).strip()
        conclusion = str(run.get("conclusion", "")).strip()
        if not name:
            continue
        if status != "completed":
            states[name] = "pending"
            continue
        states[name] = conclusion or "pending"

    statuses = _run_gh_api(statuses_path)
    for status_item in statuses:
        context = str(status_item.get("context", "")).strip()
        state = str(status_item.get("state", "")).strip()
        if context and context not in states:
            states[context] = state

    return states


def _extract_issue_number(pr_data: dict) -> str:
    body = str(pr_data.get("body", ""))
    matches = re.findall(r"(?i)closes\s+#(\d+)", body)
    return matches[0] if matches else ""


def evaluate_ci_gate(event: dict, repo: str) -> GateResult:
    owner, repo_name = _parse_repo(repo)

    check_suite = event.get("check_suite", {})
    pull_requests = check_suite.get("pull_requests", [])
    if not pull_requests:
        return GateResult(False, "当前 check_suite 未关联 PR")

    pr_number = pull_requests[0].get("number")
    if pr_number is None:
        return GateResult(False, "无法识别关联 PR 编号")

    pr = _run_gh_api(f"/repos/{owner}/{repo_name}/pulls/{pr_number}")
    head_sha = str(check_suite.get("head_sha", "")).strip()
    current_head = str(pr.get("head", {}).get("sha", "")).strip()

    if not head_sha or not current_head:
        return GateResult(False, "缺少 PR HEAD 信息")
    if head_sha != current_head:
        return GateResult(False, "check_suite 不是当前 PR HEAD，忽略")

    base_branch = str(pr.get("base", {}).get("ref", "")).strip()
    if not base_branch:
        return GateResult(False, "无法识别 PR base 分支")

    required: set[str] = set()
    try:
        required |= _required_from_branch_protection(owner, repo_name, base_branch)
    except CiGateError:
        # 分支保护接口可能因权限不足失败，继续尝试 rulesets。
        pass

    try:
        required |= _required_from_rulesets(owner, repo_name, base_branch)
    except CiGateError:
        pass

    if not required:
        return GateResult(False, "Required 检查集合为空，按 FR-08 不放行")

    states = _head_states(owner, repo_name, current_head)
    not_success: list[str] = []
    for name in sorted(required):
        state = states.get(name)
        if state != "success":
            detail = state if state is not None else "missing"
            not_success.append(f"{name}={detail}")

    if not_success:
        return GateResult(False, "; ".join(not_success))

    issue_number = _extract_issue_number(pr)
    if not issue_number:
        return GateResult(False, "未在 PR 描述中找到 Closes #issue_number")

    return GateResult(True, "全部 Required 检查为 success", issue_number=issue_number)


def _write_output(path: Path, result: GateResult) -> None:
    lines = [
        f"pass={'true' if result.passed else 'false'}",
        f"reason={result.reason}",
        f"issue_number={result.issue_number}",
    ]
    with path.open("a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="校验 PR Required CI 检查门禁")
    parser.add_argument("--event-path", required=True, help="GitHub 事件 JSON 文件路径")
    parser.add_argument("--repo", required=True, help="仓库名，格式 owner/repo")
    parser.add_argument("--output", required=True, help="GitHub Actions 输出文件路径")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    try:
        event = _load_event(Path(args.event_path))
        result = evaluate_ci_gate(event=event, repo=args.repo)
    except (CiGateError, json.JSONDecodeError) as exc:
        result = GateResult(False, f"执行异常: {exc}")

    _write_output(Path(args.output), result)
    if result.passed:
        print("CI 门禁通过。")
    else:
        print(f"CI 门禁未通过: {result.reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
