# Source Health - 2026-09-07

Generated at: 2026-09-07T09:18:21.520005+08:00

| Source | Type | State | Status | Items | Max score | Avg score | Duration | Priority | Topics |
|---|---|---|---:|---:|---:|---:|---:|---|---|
| Agent-Reach | github | keep | ok | 1 | 77 | 77.0 | 1.049s | P0 | Agent 工具生态, 网页抓取与信息入口 |
| AI News Radar | github | keep | ok | 1 | 61 | 61.0 | 0.966s | P0 | AI 信息雷达与信源治理 |
| Scrapling | github | keep | ok | 1 | 64 | 64.0 | 0.914s | P0 | 网页抓取与信息入口 |
| Hacker News | rss | observe | partial | 8 | 25 | 16.75 | 2.712s | P2 | Agent 工具生态, 网页抓取与信息入口, AI 编程与工具调用稳定性 |
| GitHub Blog | rss | keep | ok | 5 | 40 | 32.6 | 0.893s | P1 | AI 编程与工具调用稳定性, 开源安全与供应链 |
| OpenAI Blog | rss | keep | ok | 5 | 37 | 32.6 | 2.834s | P1 | 模型评估与科研智能, AI 编程与工具调用稳定性 |
| Anthropic News | rss | observe | empty | 0 | 0 | 0.0 | 0.19s | P2 | Agent 工具生态, AI 编程与工具调用稳定性 |
| Google DeepMind Blog | rss | observe | empty | 0 | 0 | 0.0 | 0.675s | P2 | 模型评估与科研智能 |
| The Batch | rss | observe | empty | 0 | 0 | 0.0 | 0.137s | P2 | 模型评估与科研智能, AI 信息雷达与信源治理 |
| Product Hunt Daily | rss | degrade | partial | 8 | 14 | 7.62 | 1.003s | P2 | AI 产品与工作流, Agent 工具生态 |
| Simon Willison | rss | keep | ok | 5 | 42 | 32.6 | 0.535s | P1 | AI 编程与工具调用稳定性, Agent 工具生态, 模型评估与科研智能 |
| Daily JS | rss | observe | empty | 0 | 0 | 0.0 | 135.33s | P3 | AI 编程与工具调用稳定性 |
| GitHub Trending Python | page | keep | ok | 1 | 51 | 51.0 | 1.968s | P1 | Agent 工具生态, 网页抓取与信息入口, AI 编程与工具调用稳定性 |
| GitHub Trending | page | keep | ok | 1 | 61 | 61.0 | 1.361s | P1 | Agent 工具生态, 网页抓取与信息入口, AI 产品与工作流 |

## Warnings

- **Hacker News**: partial / observe - trafilatura extracted empty text
- **Anthropic News**: empty / observe - no items returned
- **Google DeepMind Blog**: empty / observe - no items returned
- **The Batch**: empty / observe - no items returned
- **Product Hunt Daily**: partial / degrade - trafilatura returned empty response; trafilatura returned empty response; trafilatura returned empty response
- **Daily JS**: empty / observe - no items returned