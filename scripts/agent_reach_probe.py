from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "agent_reach.yaml"
SITE_DATA_DIR = ROOT / "site" / "data"
REPORT_DIR = ROOT / "reports"
DEFAULT_TIMEOUT = 90
TRUE_VALUES = {"1", "true", "yes", "on"}
URL_RE = re.compile(r"https?://[^\s)\]}>\"']+")


@dataclass
class ProbeResult:
    title: str
    url: str
    platform: str
    summary: str
    text: str
    score: int
    source: str = "Agent-Reach"
    status: str = "ok"


def local_now() -> datetime:
    return datetime.now(timezone(timedelta(hours=8)))


def load_config() -> dict[str, Any]:
    if not CONFIG_FILE.exists():
        return {"queries": []}
    return yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8")) or {"queries": []}


def enabled_from_env(config: dict[str, Any]) -> bool:
    flag = str(config.get("execution", {}).get("env_enable_flag", "ENABLE_AGENT_REACH"))
    return os.getenv(flag, "").lower() in TRUE_VALUES


def find_cli(config: dict[str, Any]) -> str:
    forced = os.getenv("AGENT_REACH_CLI", "").strip()
    if forced:
        return forced
    for candidate in config.get("cli", {}).get("candidates", []):
        found = shutil.which(str(candidate))
        if found:
            return found
    return ""


def safe_text(value: str, limit: int = 1800) -> str:
    value = re.sub(r"\s+", " ", value or "").strip()
    if len(value) > limit:
        return value[:limit].rstrip() + "..."
    return value


def command_for(config: dict[str, Any], query: str, platform: str, limit: int) -> list[str]:
    template = os.getenv("AGENT_REACH_COMMAND_TEMPLATE") or str(
        config.get("cli", {}).get("command_template", "agent-reach search --query {query} --platform {platform} --limit {limit}")
    )
    rendered = template.format(query=query, platform=platform, limit=limit)
    return shlex.split(rendered)


def platform_requires_login(config: dict[str, Any], platform: str, task: dict[str, Any]) -> bool:
    sensitive = {str(value) for value in config.get("platforms", {}).get("login_sensitive", [])}
    return bool(task.get("requires_login")) or platform in sensitive


def login_allowed(config: dict[str, Any]) -> bool:
    allow_config = bool(config.get("execution", {}).get("allow_login_platforms", False))
    allow_env = os.getenv("AGENT_REACH_ALLOW_LOGIN", "").lower() in TRUE_VALUES
    return allow_config or allow_env


def parse_output_to_results(task: dict[str, Any], platform: str, output: str, max_results: int) -> list[ProbeResult]:
    urls = []
    seen: set[str] = set()
    for match in URL_RE.findall(output):
        url = match.rstrip(".,;，。；")
        if url not in seen:
            urls.append(url)
            seen.add(url)
        if len(urls) >= max_results:
            break

    query = str(task.get("query", ""))
    task_name = str(task.get("name", query or "Agent-Reach task"))
    results: list[ProbeResult] = []
    if urls:
        for idx, url in enumerate(urls, start=1):
            results.append(
                ProbeResult(
                    title=f"{task_name} - {platform} result {idx}",
                    url=url,
                    platform=platform,
                    summary=f"Agent-Reach returned a {platform} result for: {query}",
                    text=safe_text(output, 900),
                    score=max(10, 40 - idx),
                )
            )
        return results

    if output.strip():
        results.append(
            ProbeResult(
                title=f"{task_name} - {platform} raw result",
                url="",
                platform=platform,
                summary=f"Agent-Reach returned text output for: {query}",
                text=safe_text(output, 1200),
                score=18,
            )
        )
    return results


def run_one(config: dict[str, Any], task: dict[str, Any], platform: str, enabled: bool, cli_path: str) -> dict[str, Any]:
    limit = int(task.get("limit") or config.get("execution", {}).get("max_results_per_task") or 6)
    query = str(task.get("query", ""))
    if platform_requires_login(config, platform, task) and not login_allowed(config):
        return {
            "platform": platform,
            "status": "skipped_login_required",
            "message": "Login-sensitive platform skipped. Run locally with AGENT_REACH_ALLOW_LOGIN=1 if appropriate.",
            "results": [],
        }

    if not enabled:
        return {
            "platform": platform,
            "status": "dry_run",
            "message": "ENABLE_AGENT_REACH is not enabled; generated execution plan only.",
            "command_preview": " ".join(command_for(config, query, platform, limit)),
            "results": [],
        }

    if not cli_path:
        return {
            "platform": platform,
            "status": "cli_not_found",
            "message": "Agent-Reach CLI was not found in PATH.",
            "command_preview": " ".join(command_for(config, query, platform, limit)),
            "results": [],
        }

    cmd = command_for(config, query, platform, limit)
    if cmd and cmd[0] in {"agent-reach", "agent_reach", "opencli"}:
        cmd[0] = cli_path
    timeout = int(os.getenv("AGENT_REACH_TIMEOUT_SECONDS") or config.get("execution", {}).get("timeout_seconds") or DEFAULT_TIMEOUT)
    try:
        completed = subprocess.run(
            cmd,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"platform": platform, "status": "timeout", "message": f"Timed out after {timeout}s", "results": []}
    except Exception as exc:  # noqa: BLE001
        return {"platform": platform, "status": "error", "message": str(exc), "results": []}

    output = "\n".join(part for part in [completed.stdout, completed.stderr] if part)
    results = parse_output_to_results(task, platform, output, limit)
    return {
        "platform": platform,
        "status": "ok" if completed.returncode == 0 else "command_failed",
        "returncode": completed.returncode,
        "command": cmd,
        "message": safe_text(output, 1000),
        "results": [result.__dict__ for result in results],
    }


def run_probe() -> dict[str, Any]:
    config = load_config()
    enabled = enabled_from_env(config)
    cli_path = find_cli(config)
    tasks_payload: list[dict[str, Any]] = []
    all_results: list[dict[str, Any]] = []

    for task in config.get("queries", []):
        task_statuses: list[dict[str, Any]] = []
        for platform in task.get("platforms", []) or ["web"]:
            status = run_one(config, task, str(platform), enabled, cli_path)
            task_statuses.append(status)
            for result in status.get("results", []):
                result["task"] = task.get("name", "")
                result["query"] = task.get("query", "")
                result["priority"] = task.get("priority", "")
                result["topic_tags"] = task.get("topic_tags", [])
                all_results.append(result)
        tasks_payload.append(
            {
                "name": task.get("name", ""),
                "query": task.get("query", ""),
                "priority": task.get("priority", ""),
                "topic_tags": task.get("topic_tags", []),
                "reason": task.get("reason", ""),
                "statuses": task_statuses,
            }
        )

    top_statuses = [status.get("status") for task in tasks_payload for status in task.get("statuses", [])]
    if all_results:
        overall_status = "ok"
    elif enabled and cli_path:
        overall_status = "no_results"
    elif enabled and not cli_path:
        overall_status = "cli_not_found"
    else:
        overall_status = "dry_run"

    return {
        "generated_at": local_now().isoformat(),
        "enabled": enabled,
        "cli_path": cli_path,
        "status": overall_status,
        "status_counts": {status: top_statuses.count(status) for status in sorted(set(top_statuses))},
        "results": all_results,
        "tasks": tasks_payload,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        f"# Agent-Reach Probe - {local_now().strftime('%Y-%m-%d')}",
        "",
        f"Generated at: {payload.get('generated_at')}",
        f"Status: {payload.get('status')}",
        f"Enabled: {payload.get('enabled')}",
        f"CLI: {payload.get('cli_path') or 'not found'}",
        "",
        "## Summary",
        "",
        f"- Results: {len(payload.get('results', []))}",
        f"- Status counts: {payload.get('status_counts', {})}",
        "",
        "## Tasks",
        "",
    ]
    for task in payload.get("tasks", []):
        lines.append(f"### {task.get('name')}")
        lines.append("")
        lines.append(f"- Query: {task.get('query')}")
        lines.append(f"- Priority: {task.get('priority')}")
        lines.append(f"- Topics: {', '.join(task.get('topic_tags', [])) or '-'}")
        lines.append(f"- Reason: {task.get('reason')}")
        for status in task.get("statuses", []):
            lines.append(f"  - {status.get('platform')}: {status.get('status')} - {status.get('message', '')}")
            if status.get("command_preview"):
                lines.append(f"    - command: `{status.get('command_preview')}`")
        lines.append("")
    if payload.get("results"):
        lines.extend(["## Results", ""])
        for result in payload.get("results", []):
            title = result.get("title", "Untitled")
            url = result.get("url", "")
            lines.append(f"### {title}")
            lines.append("")
            lines.append(f"- Platform: {result.get('platform')}")
            lines.append(f"- Query: {result.get('query')}")
            if url:
                lines.append(f"- URL: {url}")
            lines.append("")
            lines.append(result.get("summary") or result.get("text") or "")
            lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run or plan Agent-Reach probes for daily-news.")
    parser.add_argument("--json-output", default="site/data/agent_reach.json")
    parser.add_argument("--markdown-output", default="reports/agent-reach-latest.md")
    parser.add_argument("--print", action="store_true")
    args = parser.parse_args()

    payload = run_probe()
    json_path = ROOT / args.json_output if not Path(args.json_output).is_absolute() else Path(args.json_output)
    md_path = ROOT / args.markdown_output if not Path(args.markdown_output).is_absolute() else Path(args.markdown_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(payload), encoding="utf-8")
    if args.print:
        print(render_markdown(payload))
    else:
        print(f"Wrote {json_path.relative_to(ROOT)} and {md_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
