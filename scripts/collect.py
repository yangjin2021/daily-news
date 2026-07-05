from __future__ import annotations

import hashlib
import html
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

import feedparser
import trafilatura
import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCES_FILE = ROOT / "sources.yaml"
OUTPUT_DIR = ROOT / "outputs"
SITE_DIR = ROOT / "site"
SITE_DATA_DIR = SITE_DIR / "data"
DEFAULT_KEYWORDS = ["AI", "agent", "LLM", "model", "GitHub", "crawler", "research"]
USER_AGENT = "daily-news-radar/1.0 (+https://github.com/yangjin2021/daily-news)"


@dataclass
class Item:
    id: str
    source: str
    category: str
    kind: str
    title: str
    url: str
    published: str
    summary: str
    text: str
    score: int
    stars: int | None = None
    forks: int | None = None


def clean_text(value: str | None, max_chars: int = 1200) -> str:
    if not value:
        return ""
    value = html.unescape(value)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    if len(value) > max_chars:
        return value[:max_chars].rstrip() + "..."
    return value


def make_id(url: str, title: str) -> str:
    return hashlib.sha256((url or title).encode("utf-8", errors="ignore")).hexdigest()[:16]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def local_now() -> datetime:
    return datetime.now(timezone(timedelta(hours=8)))


def http_json(url: str) -> dict[str, Any]:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, headers=headers)
    with urlopen(request, timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))


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
    return data


def rank_item(title: str, summary: str, text: str, category: str, keywords: list[str]) -> int:
    haystack = f"{title} {summary} {text} {category}".lower()
    score = 0
    for keyword in keywords or DEFAULT_KEYWORDS:
        if str(keyword).lower() in haystack:
            score += 2
    if category in {"ai", "ai-dev", "ai-radar", "research-entry", "crawler", "github-trending"}:
        score += 6
    if any(word in haystack for word in ["launch", "release", "open source", "benchmark", "agent"]):
        score += 3
    return score


def collect_rss(source: dict[str, Any], keywords: list[str]) -> list[Item]:
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
                id=make_id(url, title),
                source=source.get("name", "Unknown"),
                category=source.get("category", "general"),
                kind="rss",
                title=title,
                url=url,
                published=published,
                summary=summary,
                text=text,
                score=rank_item(title, summary, text, source.get("category", "general"), keywords),
            )
        )
    return items


def collect_github(source: dict[str, Any], keywords: list[str]) -> list[Item]:
    repo = source.get("repo") or github_repo_from_url(source.get("url", ""))
    if not repo:
        return []

    try:
        data = http_json(f"https://api.github.com/repos/{repo}")
        title = f"{repo}: {clean_text(data.get('description') or source.get('note') or repo, 260)}"
        published = clean_text(data.get("pushed_at") or data.get("updated_at") or "")
        stars = int(data.get("stargazers_count") or 0)
        forks = int(data.get("forks_count") or 0)
    except (URLError, TimeoutError, ValueError, OSError) as exc:
        title = f"{repo}: {source.get('note') or 'GitHub repository'}"
        published = ""
        stars = None
        forks = None
        data = {"html_url": source.get("url", ""), "description": f"GitHub API unavailable: {exc}"}

    summary = clean_text(source.get("note") or data.get("description") or "")
    text = extract_page_text(source.get("url", data.get("html_url", "")))
    score = rank_item(title, summary, text, source.get("category", "github"), keywords)
    if stars:
        score += min(stars // 1000, 25)

    return [
        Item(
            id=make_id(source.get("url", ""), title),
            source=source.get("name", repo),
            category=source.get("category", "github"),
            kind="github",
            title=title,
            url=source.get("url") or data.get("html_url", ""),
            published=published,
            summary=summary,
            text=text,
            score=score,
            stars=stars,
            forks=forks,
        )
    ]


def github_repo_from_url(url: str) -> str:
    match = re.search(r"github\.com/([^/\s]+/[^/\s#?]+)", url)
    return match.group(1).removesuffix(".git") if match else ""


def collect_page(source: dict[str, Any], keywords: list[str]) -> list[Item]:
    title = source.get("name", source.get("url", "Page"))
    url = source.get("url", "")
    summary = clean_text(source.get("note") or "页面入口，适合后续用 Scrapling / Playwright 做深度抽取。")
    text = extract_page_text(url)
    return [
        Item(
            id=make_id(url, title),
            source=source.get("name", "Page"),
            category=source.get("category", "page"),
            kind="page",
            title=title,
            url=url,
            published=utc_now().isoformat(),
            summary=summary,
            text=text,
            score=rank_item(title, summary, text, source.get("category", "page"), keywords),
        )
    ]


def collect() -> list[Item]:
    config = load_sources()
    keywords = list(config.get("ranking", {}).get("keywords", DEFAULT_KEYWORDS))
    results: list[Item] = []
    for source in config.get("sources", []):
        source_type = source.get("type", "rss")
        try:
            if source_type == "rss":
                results.extend(collect_rss(source, keywords))
            elif source_type == "github":
                results.extend(collect_github(source, keywords))
            elif source_type == "page":
                results.extend(collect_page(source, keywords))
            else:
                print(f"Skipping unsupported source type: {source_type}")
        except Exception as exc:  # noqa: BLE001
            print(f"Source failed: {source.get('name', 'Unknown')} ({source_type}) - {exc}")
    return dedupe(results)


def dedupe(items: list[Item]) -> list[Item]:
    best: dict[str, Item] = {}
    for item in items:
        key = re.sub(r"\W+", "", (item.url or item.title).lower())
        if not key:
            continue
        if key not in best or item.score > best[key].score:
            best[key] = item
    return sorted(best.values(), key=lambda item: (item.score, item.published), reverse=True)


def item_to_dict(item: Item) -> dict[str, Any]:
    return {
        "id": item.id,
        "source": item.source,
        "category": item.category,
        "kind": item.kind,
        "title": item.title,
        "url": item.url,
        "published": item.published,
        "summary": item.summary,
        "text": item.text,
        "score": item.score,
        "stars": item.stars,
        "forks": item.forks,
    }


def render_markdown(items: list[Item]) -> str:
    now = local_now()
    date = now.strftime("%Y-%m-%d")

    lines: list[str] = []
    lines.append(f"# Daily News Radar - {date}")
    lines.append("")
    lines.append(f"Generated at: {now.isoformat()}")
    lines.append("")
    lines.append("> 这份文件是给 ChatGPT 读取的每日原料：调研入口、RSS 摘要、网页抽取片段、GitHub 仓库信号。")
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
            lines.append(f"- Type: {item.kind}")
            lines.append(f"- Score: {item.score}")
            lines.append(f"- Published: {item.published or 'Unknown'}")
            lines.append(f"- URL: {item.url}")
            if item.stars is not None:
                lines.append(f"- GitHub: {item.stars} stars / {item.forks or 0} forks")
            if item.summary:
                lines.append("")
                lines.append("**Summary**")
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


def write_site_data(items: list[Item]) -> None:
    SITE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": local_now().isoformat(),
        "total": len(items),
        "items": [item_to_dict(item) for item in items],
        "categories": counts(items, "category"),
        "sources": counts(items, "source"),
    }
    (SITE_DATA_DIR / "news.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def counts(items: list[Item], field: str) -> dict[str, int]:
    result: dict[str, int] = {}
    for item in items:
        value = str(getattr(item, field))
        result[value] = result.get(value, 0) + 1
    return dict(sorted(result.items(), key=lambda pair: pair[1], reverse=True))


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    items = collect()
    today = local_now().strftime("%Y-%m-%d")
    output_file = OUTPUT_DIR / f"{today}.md"
    output_file.write_text(render_markdown(items), encoding="utf-8")
    write_site_data(items)
    print(f"Wrote {output_file.relative_to(ROOT)} and site/data/news.json with {len(items)} items")


if __name__ == "__main__":
    main()
