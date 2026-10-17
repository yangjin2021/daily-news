# Source Health - 2026-10-17

Generated at: 2026-10-17T09:30:27.043400+08:00

| Source | Type | State | Status | Items | Max score | Avg score | Duration | Priority | Topics |
|---|---|---|---:|---:|---:|---:|---:|---|---|
| Agent-Reach | github | keep | ok | 1 | 77 | 77.0 | 1.006s | P0 | Agent 工具生态, 网页抓取与信息入口 |
| AI News Radar | github | keep | ok | 1 | 61 | 61.0 | 0.879s | P0 | AI 信息雷达与信源治理 |
| Scrapling | github | keep | ok | 1 | 64 | 64.0 | 0.983s | P0 | 网页抓取与信息入口 |
| Hacker News | rss | observe | partial | 8 | 30 | 19.88 | 3.267s | P2 | Agent 工具生态, 网页抓取与信息入口, AI 编程与工具调用稳定性 |
| GitHub Blog | rss | keep | ok | 5 | 42 | 28.4 | 0.701s | P1 | AI 编程与工具调用稳定性, 开源安全与供应链 |
| OpenAI Blog | rss | keep | ok | 5 | 33 | 28.0 | 1.692s | P1 | 模型评估与科研智能, AI 编程与工具调用稳定性 |
| Anthropic News | rss | observe | empty | 0 | 0 | 0.0 | 0.136s | P2 | Agent 工具生态, AI 编程与工具调用稳定性 |
| Google DeepMind Blog | rss | observe | empty | 0 | 0 | 0.0 | 0.604s | P2 | 模型评估与科研智能 |
| The Batch | rss | observe | empty | 0 | 0 | 0.0 | 0.077s | P2 | 模型评估与科研智能, AI 信息雷达与信源治理 |
| Product Hunt Daily | rss | degrade | partial | 8 | 10 | 5.75 | 0.605s | P2 | AI 产品与工作流, Agent 工具生态 |
| Simon Willison | rss | keep | ok | 5 | 38 | 31.0 | 0.355s | P1 | AI 编程与工具调用稳定性, Agent 工具生态, 模型评估与科研智能 |
| Daily JS | rss | observe | empty | 0 | 0 | 0.0 | 134.07s | P3 | AI 编程与工具调用稳定性 |
| GitHub Trending Python | page | keep | ok | 1 | 65 | 65.0 | 0.371s | P1 | Agent 工具生态, 网页抓取与信息入口, AI 编程与工具调用稳定性 |
| GitHub Trending | page | keep | ok | 1 | 63 | 63.0 | 1.206s | P1 | Agent 工具生态, 网页抓取与信息入口, AI 产品与工作流 |

## Warnings

- **Hacker News**: partial / observe - trafilatura returned empty response; trafilatura extracted empty text
- **Anthropic News**: empty / observe - no items returned
- **Google DeepMind Blog**: empty / observe - no items returned
- **The Batch**: empty / observe - no items returned
- **Product Hunt Daily**: partial / degrade - trafilatura returned empty response; trafilatura returned empty response; trafilatura returned empty response
- **Daily JS**: empty / observe - no items returned