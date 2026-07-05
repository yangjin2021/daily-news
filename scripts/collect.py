from __future__ import annotations

import html
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import feedparser
import trafilatura
import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCES_FILE = ROOT / "sources.yaml"
OUTPUT_DIR = ROOT / "outputs"


@dataclass
class Item:
    source: str
    category: str
    title: str
    url: str
    published: str
    summary: str
    text: str


def clean_text(value: str | None, max_chars: int = 1200) -> str:
    if not value:
        return ""
    value = html.unescape(value)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    if len(value) > max_chars:
        return value[:max_chars].rstrip() + "..."
    return value


def extract_page_text(url: str) -> str:
    """Best-effort article extraction. Fail softly so the daily run keeps going."""
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return ""
        extracted = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=False,
            favor_precision=True,
        )
        return clean_text(extracted, max_chars=1800)
    except Exception as exc:  # noqa: BLE001
        return f"[extract_error: {exc}]"


def load_sources() -> list[dict[str, Any]]:
    with SOURCES_FILE.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("sources", [])


def collect_rss(source: dict[str, Any]) -> list[Item]:
    parsed = feedparser.parse(source["url"])
    limit = int(source.get("limit", 10))
    items: list[Item] = []

    for entry in parsed.entries[:limit]:
        url = entry.get("link", "")
        title = clean_text(entry.get("title", "Untitled"), max_chars=300)
        published = clean_text(
            entry.get("published") or entry.get("updated") or "",
            max_chars=120,
        )
        summary = clean_text(entry.get("summary") or entry.get("description") or "")
        text = extract_page_text(url) if url else ""
        items.append(
            Item(
                source=source.get("name", "Unknown"),
                category=source.get("category", "general"),
                title=title,
                url=url,
                published=published,
                summary=summary,
                text=text,
            )
        )
    return items


def collect() -> list[Item]:
    results: list[Item] = []
    for source in load_sources():
        source_type = source.get("type", "rss")
        if source_type == "rss":
            results.extend(collect_rss(source))
        else:
            print(f"Skipping unsupported source type: {source_type}")
    return results


def render_markdown(items: list[Item]) -> str:
    now = datetime.now(timezone.utc)
    date = now.strftime("%Y-%m-%d")

    lines: list[str] = []
    lines.append(f"# Daily News Raw Brief - {date}")
    lines.append("")
    lines.append(f"Generated at: {now.isoformat()}")
    lines.append("")
    lines.append("> 这份文件是给 ChatGPT 读取的每日原料：标题、链接、RSS 摘要、正文抽取片段。")
    lines.append("")

    grouped: dict[str, list[Item]] = {}
    for item in items:
        grouped.setdefault(item.category, []).append(item)

    for category, category_items in sorted(grouped.items()):
        lines.append(f"## {category}")
        lines.append("")
        for idx, item in enumerate(category_items, start=1):
            lines.append(f"### {idx}. {item.title}")
            lines.append("")
            lines.append(f"- Source: {item.source}")
            lines.append(f"- Published: {item.published or 'Unknown'}")
            lines.append(f"- URL: {item.url}")
            if item.summary:
                lines.append("")
                lines.append("**RSS summary**")
                lines.append("")
                lines.append(item.summary)
            if item.text:
                lines.append("")
                lines.append("**Extracted text**")
                lines.append("")
                lines.append(item.text)
            lines.append("")
            lines.append("---")
            lines.append("")

    return "\n".join(lines)


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    items = collect()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output_file = OUTPUT_DIR / f"{today}.md"
    output_file.write_text(render_markdown(items), encoding="utf-8")
    print(f"Wrote {output_file.relative_to(ROOT)} with {len(items)} items")


if __name__ == "__main__":
    main()
