# AGENTS.md

这个仓库是一个 GPT / Codex 可调用的信息采集、筛选与报告工具。

定位：

```text
Agent-Reach      → 调研入口聚合 + 可执行探测入口
AI News Radar    → 信源筛选、去重、打分、分类
Scrapling        → 网页抽取 fallback 方向
topics.yaml      → 长期关注主题与判断框架
agent_reach.yaml → Agent-Reach 查询任务与平台策略
daily-news       → 存储、报告、网页信息站
```

## 默认调用方式

当用户要求“查一下 / 采集 / 出报告 / 今日有什么 / 帮我看某个方向”时，优先更新缓存：

```bash
python scripts/collect_with_agent_reach.py
```

然后基于缓存生成报告：

```bash
python scripts/report.py --query "<用户主题>" --from-cache --max-items 12 --depth standard --print
```

如果用户没有给主题，但要求每日信息，使用：

```bash
python scripts/report.py --query "" --from-cache --max-items 12 --depth standard --print
```

如果用户要深度研究：

```bash
python scripts/report.py --query "<用户主题>" --from-cache --max-items 20 --depth deep --print
```

如果用户要求按长期主题看，使用：

```bash
python scripts/report.py --topic "Agent 工具生态" --from-cache --max-items 12 --depth standard --print
```

## Agent-Reach 执行层

Agent-Reach 现在有两层：

1. `sources.yaml` 中的 `Agent-Reach`：追踪项目本身。
2. `agent_reach.yaml` + `scripts/agent_reach_probe.py` + `scripts/collect_with_agent_reach.py`：把“选题 → 多平台探测 → 输出结果”接进 daily-news。

默认是 dry-run / probe 模式：生成执行计划与状态报告，不自动使用登录态或个人 Cookie。

真实执行需要环境变量：

```bash
ENABLE_AGENT_REACH=1 python scripts/collect_with_agent_reach.py
```

如果实际命令不同，用模板覆盖：

```bash
AGENT_REACH_COMMAND_TEMPLATE='agent-reach search --query {query} --platform {platform} --limit {limit}' \
ENABLE_AGENT_REACH=1 python scripts/collect_with_agent_reach.py
```

小红书、B站、Twitter、Reddit 等登录敏感平台默认不在 CI 里自动启用。需要本地确认后再运行：

```bash
AGENT_REACH_ALLOW_LOGIN=1 ENABLE_AGENT_REACH=1 python scripts/agent_reach_probe.py --print
```

## 输出文件位置

- `topics.yaml`：长期关注主题、关键词、优先级和行动策略
- `agent_reach.yaml`：Agent-Reach 查询任务、平台、登录敏感策略和输出位置
- `outputs/YYYY-MM-DD.md`：每日原料，包含 source_state、topic_tags、matched_topics，也会追加 Agent-Reach 探测块
- `site/data/news.json`：网页信息站数据
- `site/data/agent_reach.json`：Agent-Reach 探测结构化结果
- `reports/agent-reach-latest.md`：Agent-Reach 探测报告
- `reports/latest-report.json`：结构化主题报告
- `site/data/source_health.json`：信源健康状态
- `reports/source-health.md`：给人读的信源健康报告

## 维护规则

- 主题明确时直接运行，不要反复问。
- 主题很宽时默认 `--max-items 12 --depth standard`。
- 用户要深挖时用 `--depth deep`。
- 运行后把关键结论直接回复给用户，并给出报告文件路径。
- 如果报告质量差，先检查 `site/data/source_health.json` 和 `site/data/agent_reach.json`，再考虑改 `sources.yaml`、`topics.yaml` 或 `agent_reach.yaml`。
- 长期观察源优先看 `observe: true`、`priority`、`source_state`、`topic_tags` 和 `watch_reason`。

## source_state 规则

- `keep`：稳定高信号，进入主视图。
- `observe`：观察 3-7 天，结合 source_health 决定升权或降权。
- `degrade`：保留但降权，只有命中强主题时才进入主报告。
- `remove`：准备删除，不再采集。
- `disabled`：临时关闭，不再采集。

## 当前长期主题

P0：

- `Agent 工具生态`
- `网页抓取与信息入口`
- `AI 信息雷达与信源治理`

P1：

- `模型评估与科研智能`
- `AI 编程与工具调用稳定性`

P2：

- `开源安全与供应链`
- `AI 产品与工作流`

## Scrapling fallback

默认稳定路径仍是 `trafilatura`。需要启用 Scrapling 时运行：

```bash
ENABLE_SCRAPLING_FALLBACK=1 python scripts/collect_with_agent_reach.py
```

注意：不要因为某个动态页面失败就删除信源。先看 `source_health`，再决定是换抓取器、降低优先级，还是保留观察。
