# Source Health - 2026-10-13

Generated at: 2026-10-13T11:48:52.892471+08:00

| Source | Type | State | Status | Items | Max score | Avg score | Duration | Priority | Topics |
|---|---|---|---:|---:|---:|---:|---:|---|---|
| Agent-Reach | github | keep | ok | 1 | 77 | 77.0 | 0.882s | P0 | Agent 工具生态, 网页抓取与信息入口 |
| AI News Radar | github | keep | ok | 1 | 61 | 61.0 | 0.862s | P0 | AI 信息雷达与信源治理 |
| Scrapling | github | keep | ok | 1 | 64 | 64.0 | 1.143s | P0 | 网页抓取与信息入口 |
| Hacker News | rss | observe | partial | 8 | 28 | 18.75 | 3.109s | P2 | Agent 工具生态, 网页抓取与信息入口, AI 编程与工具调用稳定性 |
| GitHub Blog | rss | keep | ok | 5 | 41 | 32.6 | 0.628s | P1 | AI 编程与工具调用稳定性, 开源安全与供应链 |
| OpenAI Blog | rss | keep | ok | 5 | 38 | 30.8 | 1.406s | P1 | 模型评估与科研智能, AI 编程与工具调用稳定性 |
| Anthropic News | rss | observe | empty | 0 | 0 | 0.0 | 0.175s | P2 | Agent 工具生态, AI 编程与工具调用稳定性 |
| Google DeepMind Blog | rss | observe | empty | 0 | 0 | 0.0 | 0.86s | P2 | 模型评估与科研智能 |
| The Batch | rss | observe | empty | 0 | 0 | 0.0 | 0.068s | P2 | 模型评估与科研智能, AI 信息雷达与信源治理 |
| Product Hunt Daily | rss | degrade | partial | 8 | 14 | 6.5 | 0.444s | P2 | AI 产品与工作流, Agent 工具生态 |
| Simon Willison | rss | keep | ok | 5 | 33 | 30.2 | 1.402s | P1 | AI 编程与工具调用稳定性, Agent 工具生态, 模型评估与科研智能 |
| Daily JS | rss | observe | empty | 0 | 0 | 0.0 | 136.379s | P3 | AI 编程与工具调用稳定性 |
| GitHub Trending Python | page | keep | ok | 1 | 53 | 53.0 | 1.589s | P1 | Agent 工具生态, 网页抓取与信息入口, AI 编程与工具调用稳定性 |
| GitHub Trending | page | keep | ok | 1 | 49 | 49.0 | 1.581s | P1 | Agent 工具生态, 网页抓取与信息入口, AI 产品与工作流 |

## Warnings

- **Hacker News**: partial / observe - trafilatura extracted empty text
- **Anthropic News**: empty / observe - no items returned
- **Google DeepMind Blog**: empty / observe - no items returned
- **The Batch**: empty / observe - no items returned
- **Product Hunt Daily**: partial / degrade - trafilatura returned empty response; trafilatura returned empty response; trafilatura returned empty response
- **Daily JS**: empty / observe - no items returned