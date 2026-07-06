# Daily News Radar Summary - 2026-07-06

基于 `outputs/2026-07-05.md` 生成。

## 一句话结论

今天的信息流呈现出一个清晰方向：AI 正在从“模型能力展示”转向“系统级能力验证、工具链可靠性、信息入口建设”。也就是说，真正有价值的不是单个新闻，而是围绕 Agent、数据、抓取、评估、工具协议形成的新基础设施。

## 今日核心信号

### 1. AI 评估正在进入“真实科研判断”阶段

OpenAI 发布的 GeneBench-Pro 把评估重点放在计算生物学中的复杂判断：数据是否支持问题、噪声与信号如何区分、分析路径如何修正、结果是否足以支持决策。

这说明 AI benchmark 的下一阶段不只是比拼答案正确率，而是测量 Agent 在真实研究流程中的判断链条。

**值得关注：**

- 生物、医学、科研场景会成为高级 Agent 能力验证场。
- “research taste / 研究品味”可能成为未来模型评价的重要维度。
- 对个人信息系统来说，未来不只是收集资料，而是让系统判断哪些资料真的能支撑结论。

相关链接：

- https://openai.com/index/introducing-genebench-pro
- https://openai.com/index/genebench-pro/case-studies

### 2. AI 基础设施的可靠性问题会越来越重要

OpenAI 的 core dump 文章强调，大规模 AI 服务背后的数据基础设施会遇到非常底层、罕见、难定位的问题，包括硬件静默错误与长期软件 bug。

这对 Agent 系统很重要：当 Agent 依赖搜索、缓存、插件、向量数据库和外部工具时，系统可靠性不再是附属问题，而是核心竞争力。

**可迁移到 daily-news 的启发：**

- 每个信息源需要健康状态。
- 每次抓取需要错误记录。
- 每日报告需要标注数据来源与可靠度。
- 后续应该加入 `source_health.json` 或抓取日志。

相关链接：

- https://openai.com/index/core-dump-epidemiology-data-infrastructure-bug

### 3. AI 对劳动力的影响正在从宏观讨论变成职业地图

OpenAI 的 EU workforce 报告不是简单说“AI 会替代工作”，而是按职业、制度、区域差异去分析哪些工作会增长、重组、自动化或短期变化较小。

这类内容适合成为长期追踪主题，因为它连接了 AI 能力、政策、产业和职业变化。

**建议加入长期栏目：**

- AI + 劳动力
- AI + 教育/职业再训练
- AI adoption data
- 地区差异与低成本访问

相关链接：

- https://openai.com/index/mapping-ai-jobs-transition-eu
- https://openai.com/index/how-chatgpt-adoption-has-expanded

### 4. 开源 AI 生态需要“地图”，不是更多列表

Simon Willison 关注的 Open Source AI Gap Map 很重要：它不是普通项目榜单，而是试图把开源 AI 生态拆成工具、模型、数据集、硬件、基础设施等层级。

这和 daily-news 的方向高度一致：我们不要只是抓新闻，而是建立“信息地形图”。

**对当前仓库的启发：**

- 增加 `ecosystem-map` 类别。
- 追踪 GitHub repo 不只看 star，还看它属于 AI stack 的哪一层。
- 未来可以把 sources.yaml 分成：官方源、工具源、生态地图源、社区信号源。

相关链接：

- https://simonwillison.net/2026/Jul/3/open-source-ai-gap-map/

### 5. 更强模型不一定意味着更稳定工具调用

“Better Models: Worse Tools”这条信号很值得记住：更新、更强的模型可能因为训练偏向某些特定工具接口，反而在第三方工具 schema 上更容易出错。

这对 GPT / Codex 可调用仓库特别关键。

**直接影响：**

- `AGENTS.md` 需要写得更具体。
- `scripts/report.py` 的参数 schema 应保持简单、稳定。
- 输出文件路径、缓存模式、深度参数应该避免过多隐式规则。
- 未来可以加 `--json` 和 `--markdown` 两种明确输出模式。

相关链接：

- https://simonwillison.net/2026/Jul/4/better-models-worse-tools/

### 6. AI 编程正在进入“成本可量化”的工程阶段

sqlite-utils 4.0rc2 的故事有两个信号：一是 Claude Fable 可以帮助进行复杂发布前审查；二是 AI 辅助开发的成本已经可以被精确记录，例如 prompts、commits、费用、发现的问题数量。

**对你的系统的启发：**

- 每次自动报告也应该记录“信息成本”：抓取条数、命中条数、去重后条数。
- 如果未来接模型 API，总结时要记录 token/费用。
- 把 daily-news 变成可复盘的信息工程系统，而不是一次性日报。

相关链接：

- https://simonwillison.net/2026/Jul/5/sqlite-utils-fable/

### 7. AI News Radar 与 Scrapling 已经成为你的系统方向核心

当天输出里已经包含两个与你当前仓库架构强相关的项目：

- AI News Radar：强调信源判断、抓取、去重、AI 强相关过滤、源健康和静态站点。
- Scrapling：强调现代网页抓取、自适应选择器、动态抓取、Spider、反爬适配。

这两个方向加起来，正好构成 daily-news 的下一层升级：

```text
信息入口判断
    ↓
抓取与解析
    ↓
去重与打分
    ↓
日报 / 主题报告 / 信息站
```

相关链接：

- https://github.com/AIkdb/ai-news-radar
- https://github.com/D4Vinci/Scrapling

## 今日优先级排序

| 优先级 | 主题 | 为什么重要 |
|---|---|---|
| P0 | Agent 信息入口 + Radar 架构 | 直接决定 daily-news 能不能从“抓取器”升级成“信息雷达” |
| P1 | 工具调用稳定性 | 关系到 GPT / Codex 能否可靠调用本仓库 |
| P1 | Scrapling 深度抓取 | 补 RSS 覆盖不足，扩大信息入口 |
| P2 | AI 科研评估 | 长期趋势，适合进入观察列表 |
| P2 | AI 劳动力地图 | 长期政策/产业趋势，适合周报栏目 |

## 建议下一步改造

### 1. 给每个 item 增加统一字段

建议在 `collect.py` 输出里固定以下字段：

```yaml
id:
title:
url:
source:
source_type:
category:
published:
fetched_at:
score:
relevance:
reliability:
why_it_matters:
next_action:
```

### 2. 增加三种报告视图

```text
outputs/YYYY-MM-DD.md              # 原料
reports/YYYY-MM-DD-daily.md        # 每日简报
reports/YYYY-MM-DD-topic.md        # 主题报告
site/data/news.json                # 网页数据
```

### 3. 把 report.py 变成 GPT 稳定工具

建议保留当前命令：

```bash
python scripts/report.py --query "AI Agent" --max-items 12 --depth standard --print
```

并增加：

```bash
python scripts/report.py --query "AI Agent" --format markdown
python scripts/report.py --query "AI Agent" --format json
python scripts/report.py --from-cache --query "Scrapling"
```

### 4. 增加 source health

新增：

```text
site/data/source_health.json
reports/source-health.md
```

记录：

- 最近成功抓取时间
- 错误次数
- 平均命中质量
- 是否适合继续保留

## 今日可执行任务

1. 把 `AI News Radar` 和 `Scrapling` 加为长期观察源。
2. 给 `report.py` 增加 `why_it_matters` 字段。
3. 给 `collect.py` 增加 source health 输出。
4. 在 `AGENTS.md` 里明确 GPT 调用方式。
5. 后续把 Scrapling 从“方向预留”升级成真实 fallback fetcher。

## 最终判断

今天的信息不是单点新闻，而是在指向一个共同结论：

> 个人 AI 信息系统的价值，不在于抓得更多，而在于能不能把入口、抓取、筛选、解释和复盘连成一个稳定流水线。

`daily-news` 当前已经走到这个方向上了。下一步最值得做的不是继续加源，而是把“源健康、信号打分、报告结构、工具调用稳定性”补齐。
