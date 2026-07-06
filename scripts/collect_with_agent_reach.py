from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE_DATA_DIR = ROOT / "site" / "data"
REPORT_DIR = ROOT / "reports"
OUTPUT_DIR = ROOT / "outputs"
AGENT_JSON = SITE_DATA_DIR / "agent_reach.json"
AGENT_MD = REPORT_DIR / "agent-reach-latest.md"


def local_now() -> datetime:
    return datetime.now(timezone(timedelta(hours=8)))


def run(cmd: list[str]) -> int:
    completed = subprocess.run(cmd, cwd=ROOT, text=True, check=False)
    return int(completed.returncode)


def load_agent_payload() -> dict:
    if not AGENT_JSON.exists():
        return {}
    try:
        return json.loads(AGENT_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def agent_items(payload: dict) -> list[dict]:
    now = local_now().isoformat()
    items: list[dict] = []
    for idx, result in enumerate(payload.get("results", []), start=1):
        items.append(
            {
                "id": f"agent-reach-{idx}",
                "source": "Agent-Reach Probe",
                "category": "research-entry",
                "kind": "agent_reach",
                "title": result.get("title") or result.get("query") or "Agent-Reach result",
                "url": result.get("url") or "",
                "published": payload.get("generated_at") or now,
                "summary": result.get("summary") or result.get("query") or "",
                "text": result.get("text") or "",
                "score": int(result.get("score") or 30),
                "stars": None,
                "forks": None,
                "fetched_at": now,
                "fetcher": "agent_reach",
                "fetch_error": "",
                "observed": True,
                "source_priority": result.get("priority") or "P0",
                "source_state": "keep",
                "watch_reason": "Agent-Reach 可执行入口：把选题交给多平台入口搜索，再沉淀进 daily-news。",
                "topic_tags": result.get("topic_tags") or ["Agent 工具生态", "网页抓取与信息入口"],
                "matched_topics": result.get("topic_tags") or ["Agent 工具生态", "网页抓取与信息入口"],
            }
        )
    if items:
        return items
    status = payload.get("status") or "dry_run"
    return [
        {
            "id": "agent-reach-probe-status",
            "source": "Agent-Reach Probe",
            "category": "research-entry",
            "kind": "agent_reach",
            "title": "Agent-Reach executable probe is integrated",
            "url": "agent_reach.yaml",
            "published": payload.get("generated_at") or now,
            "summary": f"Agent-Reach 执行层已接入。当前状态：{status}。启用后可把选题交给公开平台、视频、社区和网页入口搜索。",
            "text": json.dumps(payload.get("status_counts", {}), ensure_ascii=False),
            "score": 32,
            "stars": None,
            "forks": None,
            "fetched_at": now,
            "fetcher": "agent_reach_probe",
            "fetch_error": "",
            "observed": True,
            "source_priority": "P0",
            "source_state": "keep",
            "watch_reason": "Agent-Reach 可执行入口：把选题交给多平台入口搜索，再沉淀进 daily-news。",
            "topic_tags": ["Agent 工具生态", "网页抓取与信息入口"],
            "matched_topics": ["Agent 工具生态", "网页抓取与信息入口"],
        }
    ]


def append_markdown(items: list[dict]) -> None:
    today = local_now().strftime("%Y-%m-%d")
    output = OUTPUT_DIR / f"{today}.md"
    if not output.exists():
        return
    lines = ["", "## agent-reach-probe", ""]
    for idx, item in enumerate(items, start=1):
        lines.extend(
            [
                f"### {idx}. {item['title']}",
                "",
                "- Source: Agent-Reach Probe",
                "- Type: agent_reach",
                f"- Score: {item['score']}",
                "- Source state: keep",
                f"- Published: {item['published']}",
                f"- URL: {item['url']}",
                "- Fetcher: agent_reach_probe",
                "- Priority: P0",
                f"- Topic tags: {', '.join(item['topic_tags'])}",
                f"- Matched topics: {', '.join(item['matched_topics'])}",
                f"- Watch reason: {item['watch_reason']}",
                "",
                "**Summary**",
                "",
                item["summary"],
                "",
                "**Extracted text**",
                "",
                item.get("text") or "",
                "",
                "---",
                "",
            ]
        )
    current = output.read_text(encoding="utf-8")
    if "## agent-reach-probe" not in current:
        output.write_text(current.rstrip() + "\n" + "\n".join(lines), encoding="utf-8")


def patch_news_json(items: list[dict]) -> None:
    path = SITE_DATA_DIR / "news.json"
    if not path.exists():
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    existing = {item.get("id") for item in payload.get("items", [])}
    for item in items:
        if item.get("id") not in existing:
            payload.setdefault("items", []).append(item)
    payload["total"] = len(payload.get("items", []))
    payload.setdefault("categories", {})["research-entry"] = payload.get("categories", {}).get("research-entry", 0) + len(items)
    payload.setdefault("sources", {})["Agent-Reach Probe"] = len(items)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    run([sys.executable, "scripts/agent_reach_probe.py"])
    rc = run([sys.executable, "scripts/collect.py"])
    payload = load_agent_payload()
    items = agent_items(payload)
    append_markdown(items)
    patch_news_json(items)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
