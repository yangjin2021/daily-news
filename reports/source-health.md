# Source Health - 2026-10-22

Generated at: 2026-10-22T09:46:00.455527+08:00

| Source | Type | State | Status | Items | Max score | Avg score | Duration | Priority | Topics |
|---|---|---|---:|---:|---:|---:|---:|---|---|
| Agent-Reach | github | keep | ok | 1 | 77 | 77.0 | 1.004s | P0 | Agent 工具生态, 网页抓取与信息入口 |
| AI News Radar | github | keep | ok | 1 | 61 | 61.0 | 1.01s | P0 | AI 信息雷达与信源治理 |
| Scrapling | github | keep | ok | 1 | 75 | 75.0 | 1.017s | P0 | 网页抓取与信息入口 |
| Hacker News | rss | observe | partial | 8 | 28 | 20.5 | 1.986s | P2 | Agent 工具生态, 网页抓取与信息入口, AI 编程与工具调用稳定性 |
| GitHub Blog | rss | keep | ok | 5 | 33 | 26.8 | 0.659s | P1 | AI 编程与工具调用稳定性, 开源安全与供应链 |
| OpenAI Blog | rss | keep | ok | 5 | 42 | 29.0 | 1.546s | P1 | 模型评估与科研智能, AI 编程与工具调用稳定性 |
| Anthropic News | rss | observe | empty | 0 | 0 | 0.0 | 0.217s | P2 | Agent 工具生态, AI 编程与工具调用稳定性 |
| Google DeepMind Blog | rss | observe | empty | 0 | 0 | 0.0 | 0.798s | P2 | 模型评估与科研智能 |
| The Batch | rss | observe | empty | 0 | 0 | 0.0 | 0.098s | P2 | 模型评估与科研智能, AI 信息雷达与信源治理 |
| Product Hunt Daily | rss | degrade | partial | 8 | 11 | 6.25 | 0.657s | P2 | AI 产品与工作流, Agent 工具生态 |
| Simon Willison | rss | keep | ok | 5 | 36 | 33.2 | 0.46s | P1 | AI 编程与工具调用稳定性, Agent 工具生态, 模型评估与科研智能 |
| Daily JS | rss | observe | empty | 0 | 0 | 0.0 | 133.868s | P3 | AI 编程与工具调用稳定性 |
| GitHub Trending Python | page | keep | ok | 1 | 57 | 57.0 | 2.276s | P1 | Agent 工具生态, 网页抓取与信息入口, AI 编程与工具调用稳定性 |
| GitHub Trending | page | keep | ok | 1 | 53 | 53.0 | 1.237s | P1 | Agent 工具生态, 网页抓取与信息入口, AI 产品与工作流 |

## Warnings

- **Hacker News**: partial / observe - trafilatura extracted empty text
- **Anthropic News**: empty / observe - no items returned
- **Google DeepMind Blog**: empty / observe - no items returned
- **The Batch**: empty / observe - no items returned
- **Product Hunt Daily**: partial / degrade - trafilatura returned empty response; trafilatura returned empty response; trafilatura returned empty response
- **Daily JS**: empty / observe - no items returned