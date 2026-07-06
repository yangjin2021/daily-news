# Source Health - 2026-07-06

Generated at: 2026-07-06T21:03:27.572717+08:00

| Source | Type | State | Status | Items | Max score | Avg score | Duration | Priority | Topics |
|---|---|---|---:|---:|---:|---:|---:|---|---|
| Agent-Reach | github | keep | ok | 1 | 77 | 77.0 | 1.196s | P0 | Agent 工具生态, 网页抓取与信息入口 |
| Agent-Reach Probe | agent_reach | keep | skipped | 0 | 0 | 0.0 | 0.0s | P0 | Agent 工具生态, 网页抓取与信息入口, AI 产品与工作流 |
| AI News Radar | github | keep | ok | 1 | 61 | 61.0 | 1.005s | P0 | AI 信息雷达与信源治理 |
| Scrapling | github | keep | ok | 1 | 64 | 64.0 | 1.156s | P0 | 网页抓取与信息入口 |
| Hacker News | rss | observe | partial | 8 | 27 | 16.25 | 4.865s | P2 | Agent 工具生态, 网页抓取与信息入口, AI 编程与工具调用稳定性 |
| GitHub Blog | rss | keep | ok | 5 | 38 | 28.8 | 0.992s | P1 | AI 编程与工具调用稳定性, 开源安全与供应链 |
| OpenAI Blog | rss | keep | ok | 5 | 52 | 33.4 | 3.18s | P1 | 模型评估与科研智能, AI 编程与工具调用稳定性 |
| Anthropic News | rss | observe | empty | 0 | 0 | 0.0 | 5.439s | P2 | Agent 工具生态, AI 编程与工具调用稳定性 |
| Google DeepMind Blog | rss | observe | empty | 0 | 0 | 0.0 | 0.683s | P2 | 模型评估与科研智能 |
| The Batch | rss | observe | empty | 0 | 0 | 0.0 | 0.132s | P2 | 模型评估与科研智能, AI 信息雷达与信源治理 |
| Product Hunt Daily | rss | degrade | ok | 8 | 22 | 13.75 | 4.857s | P2 | AI 产品与工作流, Agent 工具生态 |
| Simon Willison | rss | keep | ok | 5 | 42 | 31.0 | 0.601s | P1 | AI 编程与工具调用稳定性, Agent 工具生态, 模型评估与科研智能 |
| Daily JS | rss | observe | empty | 0 | 0 | 0.0 | 136.119s | P3 | AI 编程与工具调用稳定性 |
| GitHub Trending Python | page | keep | ok | 1 | 75 | 75.0 | 1.594s | P1 | Agent 工具生态, 网页抓取与信息入口, AI 编程与工具调用稳定性 |
| GitHub Trending | page | keep | ok | 1 | 68 | 68.0 | 1.417s | P1 | Agent 工具生态, 网页抓取与信息入口, AI 产品与工作流 |

## Warnings

- **Agent-Reach Probe**: skipped / keep - unsupported source type: agent_reach
- **Hacker News**: partial / observe - trafilatura extracted empty text; trafilatura extracted empty text; trafilatura extracted empty text
- **Anthropic News**: empty / observe - no items returned
- **Google DeepMind Blog**: empty / observe - no items returned
- **The Batch**: empty / observe - no items returned
- **Daily JS**: empty / observe - no items returned