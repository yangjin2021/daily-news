from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

from collect import Item, clean_text, collect, item_to_dict, local_now


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports"
SITE_DATA = ROOT / "site" / "data" / "news.json"
TOPICS_FILE = ROOT / "topics.yaml"


def slugify(value: str) -> str:
    value = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", value.strip().lower(), flags=re.UNICODE)
    value = re.sub(r"-+", "-", value).strip("-")
    return value[:60] or "daily-report"


def load_topics() -> list[dict[str, Any]]:
    if not TOPICS_FILE.exists():
        return []
    data = yaml.safe_load(TOPICS_FILE.read_text(encoding="utf-8")) or {}
    return list(data.get("topics", []))


def load_cached_items() -> list[Item]:
    if not SITE_DATA.exists():
        return []
    payload = json.loads(SITE_DATA.read_text(encoding="utf-8"))
    items: list[Item] = []
    for raw in payload.get("items", []):
        allowed = {field.name for field in Item.__dataclass_fields__.values()}
        data = {key: raw.get(key) for key in allowed if key in raw}
        items.append(Item(**data))
    return items


def split_terms(query: str) -> list[str]:
    terms = re.split(r"[\s,，、/|]+", query.strip())
    return [term.lower() for term in terms if len(term.strip()) >= 2]


def safe_lower(value: str | None) -> str:
    return (value or "").lower()


def topic_matches_query(topic: dict[str, Any], terms: list[str]) -> bool:
    if not terms:
        return False
    haystack = " ".join(
        [
            str(topic.get("name", "")),
            str(topic.get("intent", "")),
            " ".join(str(value) for value in topic.get("keywords", [])),
            " ".join(str(value) for value in topic.get("categories", [])),
        ]
    ).lower()
    return any(term in haystack for term in terms)


def matched_topic_names(item: Item, topics: list[dict[str, Any]], query: str = "") -> list[str]:
    existing = list(dict.fromkeys([*(item.matched_topics or []), *(item.topic_tags or [])]))
    if existing:
        return existing
    haystack = f"{item.title} {item.summary} {item.text} {item.category}".lower()
    result: list[str] = []
    for topic in topics:
        topic_name = str(topic.get("name", ""))
        categories = {str(value).lower() for value in topic.get("categories", [])}
        keywords = [str(value).lower() for value in topic.get("keywords", [])]
        if safe_lower(item.category) in categories or any(keyword and keyword in haystack for keyword in keywords):
            result.append(topic_name)
    return result


def match_score(item: Item, terms: list[str], topics: list[dict[str, Any]]) -> int:
    if not terms:
        return item.score

    title = safe_lower(item.title)
    summary = safe_lower(item.summary)
    text = safe_lower(item.text)
    meta = f"{item.source} {item.category} {item.kind} {item.source_state} {' '.join(item.topic_tags)} {' '.join(item.matched_topics)}".lower()
    score = 0
    for term in terms:
        if term in title:
            score += 12
        if term in summary:
            score += 6
        if term in text:
            score += 3
        if term in meta:
            score += 7
    item_topics = set(matched_topic_names(item, topics))
    query_topics = {str(topic.get("name", "")) for topic in topics if topic_matches_query(topic, terms)}
    if item_topics & query_topics:
        score += 16
    return score + item.score


def filter_items(items: list[Item], query: str, categories: list[str], topics_filter: list[str], max_items: int, topics: list[dict[str, Any]]) -> list[tuple[Item, int]]:
    terms = split_terms(query)
    category_set = {category.lower() for category in categories}
    topic_set = {topic.lower() for topic in topics_filter}
    ranked: list[tuple[Item, int]] = []
    for item in items:
        if category_set and item.category.lower() not in category_set:
            continue
        item_topics = [topic.lower() for topic in matched_topic_names(item, topics, query)]
        if topic_set and not topic_set.intersection(item_topics):
            continue
        score = match_score(item, terms, topics)
        if not terms or score > item.score or topic_set:
            ranked.append((item, score))

    if not ranked and terms:
        ranked = [(item, item.score) for item in items if not category_set or item.category.lower() in category_set]

    ranked.sort(key=lambda pair: pair[1], reverse=True)
    return ranked[:max_items]


def reason_for(item: Item, query: str, topics: list[dict[str, Any]]) -> str:
    terms = split_terms(query)
    matched = [term for term in terms if term in f"{item.title} {item.summary} {item.text}".lower()]
    if matched:
        return f"命中关键词：{', '.join(matched[:4])}"
    item_topics = matched_topic_names(item, topics, query)
    if item_topics:
        return f"命中长期主题：{', '.join(item_topics[:3])}"
    if item.kind == "github":
        return "GitHub 项目入口，可继续评估是否接入工作流"
    if item.kind == "page":
        return "网页入口，适合继续深度抽取"
    return "RSS / 页面内容信号较强，适合纳入今日阅读"


def why_it_matters(item: Item, query: str = "") -> str:
    category = safe_lower(item.category)
    title = safe_lower(item.title)
    summary = safe_lower(item.summary)
    text = safe_lower(item.text)
    haystack = f"{title} {summary} {text}"

    if item.watch_reason:
        return item.watch_reason
    if category == "research-entry" or "agent-reach" in title:
        return "它代表调研入口层：决定 Agent 能接触哪些网页、社区、仓库、视频和趋势源。"
    if category == "ai-radar" or "news radar" in title:
        return "它代表筛选层：把信息源判断、去重、AI 强相关过滤、源健康和静态发布串成 pipeline。"
    if category == "crawler" or "scrapling" in title:
        return "它代表抓取层：补足 RSS 覆盖不到的网页，并为动态页面、反爬和深度抽取提供 fallback。"
    if category == "github-trending":
        return "它是发现层入口：可以帮助系统从每日趋势里发现新的工具、项目和可接入工作流。"
    if "benchmark" in haystack or "eval" in haystack:
        return "它说明 AI 正在从能力展示进入可验证、可复盘、可比较的评估阶段。"
    if "tool" in haystack or "schema" in haystack or "agent" in haystack:
        return "它影响 GPT / Agent 工具调用稳定性，关系到这个仓库能不能被可靠地自动调用。"
    if item.kind == "github" and item.stars:
        return f"它是可追踪的 GitHub 项目信号，当前约 {item.stars} stars，可继续观察增长和接入价值。"
    if query.strip():
        return f"它与“{query.strip()}”相关，可作为主题报告里的证据或后续深挖入口。"
    return "它是今日信息流中的有效信号，可用于日报摘要、选题判断或后续追踪。"


def next_action_for(item: Item) -> str:
    category = safe_lower(item.category)
    state = safe_lower(item.source_state)
    if state == "degrade":
        return "仅在命中强主题时保留；观察 7 天后决定是否删除或恢复。"
    if state == "observe":
        return "继续观察 7 天，结合 source_health 判断升权、降权或删除。"
    if category in {"research-entry", "ai-radar", "crawler", "github-trending"}:
        return "评估是否接入 daily-news 工作流，并观察 7 天信号质量。"
    if item.kind == "github":
        return "查看 README、release、issues，判断是否值得长期观察。"
    if item.kind == "page":
        return "用网页抽取或 Scrapling fallback 做二次抓取。"
    return "纳入今日摘要；若连续出现，再升级为长期观察源。"


def clipped(value: str, depth: str) -> str:
    limits = {"brief": 260, "standard": 520, "deep": 1100}
    return clean_text(value, max_chars=limits.get(depth, 520))


def summarize_topics(ranked: list[tuple[Item, int]], topics: list[dict[str, Any]]) -> list[str]:
    counts: dict[str, int] = {}
    for item, _score in ranked:
        for topic in matched_topic_names(item, topics):
            counts[topic] = counts.get(topic, 0) + 1
    return [f"- {topic}: {count} 条" for topic, count in sorted(counts.items(), key=lambda pair: pair[1], reverse=True)[:8]]


def render_report(query: str, ranked: list[tuple[Item, int]], total: int, depth: str, fresh: bool, topics: list[dict[str, Any]]) -> str:
    now = local_now()
    title = query.strip() or "全部信息"
    lines: list[str] = [
        f"# 一键信息报告：{title}",
        "",
        f"- 生成时间：{now.isoformat()}",
        f"- 数据模式：{'实时采集' if fresh else '读取缓存'}",
        f"- 候选信息：{total} 条",
        f"- 入选信息：{len(ranked)} 条",
        "",
        "## 主题覆盖",
        "",
    ]
    topic_lines = summarize_topics(ranked, topics)
    lines.extend(topic_lines or ["- 暂无明显长期主题命中"])
    lines.extend(["", "## 结论速览", ""])

    if not ranked:
        lines.extend(["没有找到匹配内容。", ""])
        return "\n".join(lines)

    for idx, (item, score) in enumerate(ranked[:5], start=1):
        lines.append(f"{idx}. [{item.title}]({item.url})")
        lines.append(f"   - 来源：{item.source} / {item.category} / {item.kind} / {item.source_state}")
        lines.append(f"   - 主题：{', '.join(matched_topic_names(item, topics, query)) or '未归类'}")
        lines.append(f"   - 推荐理由：{reason_for(item, query, topics)}")
        lines.append(f"   - 为什么重要：{why_it_matters(item, query)}")
        lines.append(f"   - 下一步：{next_action_for(item)}")
        lines.append(f"   - 报告分：{score}")
    lines.append("")

    grouped: dict[str, list[tuple[Item, int]]] = {}
    for item, score in ranked:
        grouped.setdefault(item.category, []).append((item, score))

    lines.extend(["## 分组详情", ""])
    for category, pairs in grouped.items():
        lines.extend([f"### {category}", ""])
        for item, score in pairs:
            lines.append(f"#### [{item.title}]({item.url})")
            lines.append("")
            lines.append(f"- 来源：{item.source}")
            lines.append(f"- 类型：{item.kind}")
            lines.append(f"- source_state：{item.source_state}")
            lines.append(f"- 报告分：{score}")
            lines.append(f"- 主题：{', '.join(matched_topic_names(item, topics, query)) or '未归类'}")
            lines.append(f"- 为什么重要：{why_it_matters(item, query)}")
            lines.append(f"- 下一步：{next_action_for(item)}")
            if getattr(item, "fetcher", ""):
                lines.append(f"- 抽取器：{item.fetcher}")
            if getattr(item, "fetch_error", ""):
                lines.append(f"- 抽取警告：{item.fetch_error}")
            if item.stars is not None:
                lines.append(f"- GitHub：{item.stars} stars / {item.forks or 0} forks")
            if item.published:
                lines.append(f"- 时间：{item.published}")
            summary = clipped(item.summary, depth)
            text = clipped(item.text, depth)
            if summary:
                lines.extend(["", "**摘要**", "", summary])
            if text and depth != "brief":
                lines.extend(["", "**抽取内容**", "", text])
            lines.append("")

    lines.extend(
        [
            "## 给 GPT 的下一步",
            "",
            "- 如果你要写日报：优先用“结论速览”的前 5 条做主线。",
            "- 如果你要做选题：优先看主题覆盖里的 P0/P1 长期主题。",
            "- 如果你要继续深挖：拿条目的 URL 再做二次网页读取和交叉验证。",
            "- 如果你要维护系统：先看 `site/data/source_health.json` 和 `reports/source-health.md`。",
            "",
        ]
    )
    return "\n".join(lines)


def write_json_report(path: Path, query: str, ranked: list[tuple[Item, int]], topics: list[dict[str, Any]]) -> None:
    payload: dict[str, Any] = {
        "query": query,
        "generated_at": local_now().isoformat(),
        "topic_coverage": summarize_topics(ranked, topics),
        "items": [
            {
                **item_to_dict(item),
                "report_score": score,
                "matched_topics": matched_topic_names(item, topics, query),
                "why_it_matters": why_it_matters(item, query),
                "next_action": next_action_for(item),
            }
            for item, score in ranked
        ],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Collect sources and generate a GPT-ready report.")
    parser.add_argument("-q", "--query", default="", help="要报告的主题，例如：AI Agent、网页抓取、GitHub 热门项目")
    parser.add_argument("--category", action="append", default=[], help="只看某个分类，可重复传入")
    parser.add_argument("--topic", action="append", default=[], help="只看某个长期主题，可重复传入")
    parser.add_argument("--max-items", type=int, default=12, help="报告最多包含多少条")
    parser.add_argument("--depth", choices=["brief", "standard", "deep"], default="standard", help="报告详细程度")
    parser.add_argument("--from-cache", action="store_true", help="不重新采集，只读取 site/data/news.json")
    parser.add_argument("--output", default="", help="Markdown 输出路径，默认 reports/<date>-<query>.md")
    parser.add_argument("--json-output", default="", help="可选 JSON 输出路径")
    parser.add_argument("--print", action="store_true", help="同时打印 Markdown 报告，方便 GPT 直接读取")
    args = parser.parse_args()

    topics = load_topics()
    fresh = not args.from_cache
    items = load_cached_items() if args.from_cache else collect()
    ranked = filter_items(items, args.query, args.category, args.topic, max(1, args.max_items), topics)
    report = render_report(args.query, ranked, len(items), args.depth, fresh, topics)

    REPORT_DIR.mkdir(exist_ok=True)
    date = local_now().strftime("%Y-%m-%d")
    output = Path(args.output) if args.output else REPORT_DIR / f"{date}-{slugify(args.query)}.md"
    if not output.is_absolute():
        output = ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")

    json_output = Path(args.json_output) if args.json_output else REPORT_DIR / "latest-report.json"
    if not json_output.is_absolute():
        json_output = ROOT / json_output
    write_json_report(json_output, args.query, ranked, topics)

    if args.print:
        sys.stdout.write(report)
        sys.stdout.write("\n")
    else:
        print(f"Wrote {output.relative_to(ROOT)} with {len(ranked)} selected items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
