from __future__ import annotations

import hashlib
import html
import json
import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from time import perf_counter
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

import feedparser
import trafilatura
import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCES_FILE = ROOT / "sources.yaml"
OUTPUT_DIR = ROOT / "outputs"
REPORT_DIR = ROOT / "reports"
SITE_DIR = ROOT / "site"
SITE_DATA_DIR = SITE_DIR / "data"
DEFAULT_KEYWORDS = ["AI", "agent", "LLM", "model", "GitHub", "crawler", "research"]
USER_AGENT = "daily-news-radar/1.1 (+https://github.com/yangjin2021/daily-news)"
ENABLE_SCRAPLING_FALLBACK = os.getenv("ENABLE_SCRAPLING_FALLBACK", "").lower() in {"1", "true", "yes"}


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
    fetched_at: str = ""
    fetcher: str = ""
    fetch_error: str = ""
    observed: bool = False
    source_priority: str = ""
    watch_reason: str = ""


@dataclass
class SourceHealth:
    name: str
    type: str
    category: str
    url: str
    observed: bool
    priority: str
    status: str
    item_count: int
    error: str
    started_at: str
    finished_at: str
    duration_seconds: float
    max_score: int
    average_score: float


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


def extract_with_trafilatura(url: str) -> tuple[str, str]:
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return "", "trafilatura returned empty response"
    extracted = trafilatura.extract(
        downloaded,
        include_comments=False,
        include_tables=False,
        favor_precision=True,
    )
    text = clean_text(extracted, max_chars=1800)
    if not text:
        return "", "trafilatura extracted empty text"
    return text, ""


def extract_with_scrapling(url: str) -> tuple[str, str]:
    """Optional fallback. Enabled with ENABLE_SCRAPLING_FALLBACK=1 and an installed scrapling package."""
    try:
        from scrapling.fetchers import Fetcher  # type: ignore
    except Exception as exc:  # noqa: BLE001
        return "", f"scrapling unavailable: {exc}"

    try:
        page = Fetcher.fetch(url)
    except AttributeError:
        try:
            page = Fetcher().get(url)
        except Exception as exc:  # noqa: BLE001
            return "", f"scrapling fetch failed: {exc}"
    except Exception as exc:  # noqa: BLE001
        return "", f"scrapling fetch failed: {exc}"

    text = clean_text(getattr(page, "text", "") or getattr(page, "body", ""), max_chars=1800)
    if not text:
        return "", "scrapling extracted empty text"
    return text, ""


def extract_page_text(url: str) -> tuple[str, str, str]:
    """Best-effort article extraction.

    Returns (text, fetcher, error). Trafilatura is the default stable path.
    Scrapling is wired as an optional fallback so the workflow does not break if
    the package is not installed or a dynamic page needs deeper extraction later.
    """
    if not url:
        return "", "none", "empty url"

    errors: list[str] = []
    try:
        text, error = extract_with_trafilatura(url)
        if text:
            return text, "trafilatura", ""
        if error:
            errors.append(error)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"trafilatura failed: {exc}")

    if ENABLE_SCRAPLING_FALLBACK:
        text, error = extract_with_scrapling(url)
        if text:
            return text, "scrapling", ""
        if error:
            errors.append(error)

    return "", "none", "; ".join(errors)


def load_sources() -> dict[str, Any]:
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


def source_meta(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "observed": bool(source.get("observe", False)),
        "source_priority": str(source.get("priority", "")),
        "watch_reason": str(source.get("watch_reason", "")),
    }


def collect_rss(source: dict[str, Any], keywords: list[str]) -> list[Item]:
    parsed = feedparser.parse(source["url"])
    limit = int(source.get("limit", 10))
    items: list[Item] = []
    meta = source_meta(source)

    for entry in parsed.entries[:limit]:
        url = entry.get("link", "")
        title = clean_text(entry.get("title", "Untitled"), max_chars=300)
        published = clean_text(
            entry.get("published") or entry.get("updated") or "",
            max_chars=120,
        )
        summary = clean_text(entry.get("summary") or entry.get("description") or "")
        text, fetcher, fetch_error = extract_page_text(url)
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
                fetched_at=local_now().isoformat(),
                fetcher=fetcher,
                fetch_error=fetch_error,
                **meta,
            )
        )
    return items


def collect_github(source: dict[str, Any], keywords: list[str]) -> list[Item]:
    repo = source.get("repo") or github_repo_from_url(source.get("url", ""))
    if not repo:
        return []

    meta = source_meta(source)
    fetch_error = ""
    fetcher = "trafilatura"
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
        fetch_error = f"GitHub API unavailable: {exc}"

    summary = clean_text(source.get("note") or data.get("description") or "")
    text, page_fetcher, page_error = extract_page_text(source.get("url", data.get("html_url", "")))
    fetcher = page_fetcher
    if page_error:
        fetch_error = "; ".join(part for part in [fetch_error, page_error] if part)
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
            fetched_at=local_now().isoformat(),
            fetcher=fetcher,
            fetch_error=fetch_error,
            **meta,
        )
    ]


def github_repo_from_url(url: str) -> str:
    match = re.search(r"github\.com/([^/\s]+/[^/\s#?]+)", url)
    return match.group(1).removesuffix(".git") if match else ""


def collect_page(source: dict[str, Any], keywords: list[str]) -> list[Item]:
    title = source.get("name", source.get("url", "Page"))
    url = source.get("url", "")
    summary = clean_text(source.get("note") or "页面入口，适合后续用 Scrapling / Playwright 做深度抽取。")
    text, fetcher, fetch_error = extract_page_text(url)
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
            fetched_at=local_now().isoformat(),
            fetcher=fetcher,
            fetch_error=fetch_error,
            **source_meta(source),
        )
    ]


def collect_source(source: dict[str, Any], keywords: list[str]) -> tuple[list[Item], SourceHealth]:
    source_type = source.get("type", "rss")
    started = local_now()
    start_perf = perf_counter()
    status = "ok"
    error = ""
    items: list[Item] = []

    try:
        if source_type == "rss":
            items = collect_rss(source, keywords)
        elif source_type == "github":
            items = collect_github(source, keywords)
        elif source_type == "page":
            items = collect_page(source, keywords)
        else:
            status = "skipped"
            error = f"unsupported source type: {source_type}"
            print(f"Skipping unsupported source type: {source_type}")
    except Exception as exc:  # noqa: BLE001
        status = "error"
        error = str(exc)
        print(f"Source failed: {source.get('name', 'Unknown')} ({source_type}) - {exc}")

    if status == "ok" and not items:
        status = "empty"

    fetch_errors = [item.fetch_error for item in items if item.fetch_error]
    if status == "ok" and fetch_errors:
        status = "partial"
        error = "; ".join(fetch_errors[:3])

    finished = local_now()
    scores = [item.score for item in items]
    health = SourceHealth(
        name=source.get("name", "Unknown"),
        type=source_type,
        category=source.get("category", "general"),
        url=source.get("url", ""),
        observed=bool(source.get("observe", False)),
        priority=str(source.get("priority", "")),
        status=status,
        item_count=len(items),
        error=clean_text(error, max_chars=500),
        started_at=started.isoformat(),
        finished_at=finished.isoformat(),
        duration_seconds=round(perf_counter() - start_perf, 3),
        max_score=max(scores) if scores else 0,
        average_score=round(sum(scores) / len(scores), 2) if scores else 0.0,
    )
    return items, health


def collect_with_health() -> tuple[list[Item], list[SourceHealth]]:
    config = load_sources()
    keywords = list(config.get("ranking", {}).get("keywords", DEFAULT_KEYWORDS))
    results: list[Item] = []
    health: list[SourceHealth] = []
    for source in config.get("sources", []):
        source_items, source_health = collect_source(source, keywords)
        results.extend(source_items)
        health.append(source_health)
    return dedupe(results), health


def collect() -> list[Item]:
    items, _health = collect_with_health()
    return items


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
    return asdict(item)


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
            if item.fetcher:
                lines.append(f"- Fetcher: {item.fetcher}")
            if item.source_priority:
                lines.append(f"- Priority: {item.source_priority}")
            if item.watch_reason:
                lines.append(f"- Watch reason: {item.watch_reason}")
            if item.fetch_error:
                lines.append(f"- Fetch warning: {item.fetch_error}")
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


def write_site_data(items: list[Item], health: list[SourceHealth] | None = None) -> None:
    SITE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": local_now().isoformat(),
        "total": len(items),
        "items": [item_to_dict(item) for item in items],
        "categories": counts(items, "category"),
        "sources": counts(items, "source"),
        "source_health": [asdict(row) for row in health or []],
    }
    (SITE_DATA_DIR / "news.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_source_health(health: list[SourceHealth]) -> None:
    SITE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(exist_ok=True)
    payload = {
        "generated_at": local_now().isoformat(),
        "sources": [asdict(row) for row in health],
        "summary": counts_health(health),
    }
    (SITE_DATA_DIR / "source_health.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (REPORT_DIR / "source-health.md").write_text(render_source_health_markdown(health), encoding="utf-8")


def render_source_health_markdown(health: list[SourceHealth]) -> str:
    now = local_now()
    lines = [
        f"# Source Health - {now.strftime('%Y-%m-%d')}",
        "",
        f"Generated at: {now.isoformat()}",
        "",
        "| Source | Type | Status | Items | Max score | Avg score | Duration | Priority |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in health:
        lines.append(
            f"| {row.name} | {row.type} | {row.status} | {row.item_count} | {row.max_score} | "
            f"{row.average_score} | {row.duration_seconds}s | {row.priority or '-'} |"
        )
    failed = [row for row in health if row.status in {"error", "partial", "empty"}]
    if failed:
        lines.extend(["", "## Warnings", ""])
        for row in failed:
            lines.append(f"- **{row.name}**: {row.status} - {row.error or 'no items returned'}")
    return "\n".join(lines)


def counts(items: list[Item], field: str) -> dict[str, int]:
    result: dict[str, int] = {}
    for item in items:
        value = str(getattr(item, field))
        result[value] = result.get(value, 0) + 1
    return dict(sorted(result.items(), key=lambda pair: pair[1], reverse=True))


def counts_health(health: list[SourceHealth]) -> dict[str, int]:
    result: dict[str, int] = {}
    for row in health:
        result[row.status] = result.get(row.status, 0) + 1
    return dict(sorted(result.items(), key=lambda pair: pair[1], reverse=True))


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    items, health = collect_with_health()
    today = local_now().strftime("%Y-%m-%d")
    output_file = OUTPUT_DIR / f"{today}.md"
    output_file.write_text(render_markdown(items), encoding="utf-8")
    write_site_data(items, health)
    write_source_health(health)
    print(
        f"Wrote {output_file.relative_to(ROOT)}, site/data/news.json, "
        f"and site/data/source_health.json with {len(items)} items"
    )


if __name__ == "__main__":
    main()
