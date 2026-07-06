# AGENTS.md

这个仓库是一个 GPT / Codex 可调用的信息采集与报告工具。

定位：

```text
Agent-Reach      → 调研入口聚合
AI News Radar    → 信源筛选、去重、打分、分类
Scrapling        → 网页抽取 fallback 方向
daily-news       → 存储、报告、网页信息站
```

## 默认调用方式

当用户要求“查一下 / 采集 / 出报告 / 今日有什么 / 帮我看某个方向”时，不要只读旧文件，优先运行：

```bash
python scripts/report.py --query "<用户主题>" --max-items 12 --depth standard --print
```

如果用户没有给主题，但要求每日信息，使用：

```bash
python scripts/report.py --query "" --max-items 12 --depth standard --print
```

如果用户要快一点，或者已经确认只看缓存：

```bash
python scripts/report.py --query "<用户主题>" --from-cache --print
```

如果用户要深度研究：

```bash
python scripts/report.py --query "<用户主题>" --max-items 20 --depth deep --print
```

如果用户要简报：

```bash
python scripts/report.py --query "<用户主题>" --max-items 8 --depth brief --print
```

## 输出文件位置

- `reports/YYYY-MM-DD-<topic>.md`：给人和 GPT 读的主题报告
- `reports/latest-report.json`：结构化结果，包含 `why_it_matters` 和 `next_action`
- `outputs/YYYY-MM-DD.md`：全量每日原料
- `site/data/news.json`：网页信息站数据
- `site/data/source_health.json`：信源健康状态
- `reports/source-health.md`：给人读的信源健康报告

## 维护规则

- 主题明确时直接运行，不要反复问。
- 主题很宽时默认 `--max-items 12 --depth standard`。
- 用户要深挖时用 `--depth deep`。
- 用户要简报时用 `--depth brief`。
- 运行后把报告里的关键结论直接回复给用户，并给出报告文件路径。
- 如果报告质量差，先检查 `site/data/source_health.json`，再考虑改 `sources.yaml`。
- 长期观察源优先看 `observe: true`、`priority` 和 `watch_reason`。

## 长期观察源

当前 P0 长期观察源：

- `Agent-Reach`：调研入口聚合。
- `AI News Radar`：信息雷达 pipeline。
- `Scrapling`：网页抓取与 fallback 能力。

P1 发现源：

- `GitHub Trending`
- `GitHub Trending Python`

## Scrapling fallback

默认稳定路径仍是 `trafilatura`。如果环境已经安装 Scrapling，并且需要把 Scrapling 作为网页抽取 fallback，运行前设置：

```bash
ENABLE_SCRAPLING_FALLBACK=1 python scripts/collect.py
```

或：

```bash
ENABLE_SCRAPLING_FALLBACK=1 python scripts/report.py --query "网页抓取" --depth deep --print
```

注意：不要因为某个动态页面失败就删除信源。先看 `source_health`，再决定是换抓取器、降低优先级，还是保留观察。
