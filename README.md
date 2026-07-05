# Daily News Radar

一个给 ChatGPT 和你自己阅读的信息收集站。

目标不是把网页抓下来堆成垃圾，而是把网页、仓库、RSS 和趋势入口变成每天可筛选、可复盘、可继续深挖的知识流。

这版把三个方向合在一起：

- Agent-Reach：调研入口聚合，先把网页、社区、仓库、趋势入口接进来。
- AI News Radar：按来源抓取、去重、打分、分类，形成 24 小时信息雷达。
- Scrapling：把 RSS 抓不到的页面当作网页抽取入口，后续可替换成更强的 Scrapling 深度抓取。

## 工作流

```text
sources.yaml
    ↓
scripts/collect.py
    ↓
outputs/YYYY-MM-DD.md        # 给 ChatGPT 读取
site/data/news.json          # 给网页读取
site/index.html              # 信息收集站
```

## 目录

```text
sources.yaml                 # 内容来源：RSS / 网站 / GitHub / 博客
scripts/collect.py           # 采集与清洗脚本
outputs/                     # 每日生成的 Markdown 简报原料
site/                        # GitHub Pages 信息面板
.github/workflows/daily.yml  # GitHub Actions 自动运行
requirements.txt             # Python 依赖
```

## 本地运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/collect.py
```

生成结果会出现在：

```text
outputs/YYYY-MM-DD.md
site/data/news.json
```

## 自动运行

GitHub Actions 默认每天北京时间早上 7:30 左右运行一次，也可以在 GitHub 的 Actions 页面手动运行。运行后会更新 Markdown 原料，并部署 `site/` 到 GitHub Pages。

如果第一次启用 Pages，需要在仓库设置里选择：

```text
Settings → Pages → Build and deployment → GitHub Actions
```

## 和 ChatGPT 配合

每天你可以直接在 ChatGPT 里说：

> 读取我的 daily-news 仓库，整理今天值得看的内容。

我会把 `outputs/` 里的 Markdown 变成你的每日阅读界面：摘要、分组、洞察、选题、待深挖方向。

## 下一步

后续可以继续加：

- Playwright：打开动态网页
- Scrapling：更强的页面提取和反爬适配
- SQLite：保存历史全文
- 向量检索：让 ChatGPT 按主题回忆旧内容
- 选题生成：把每日内容转成文章、视频、播客脚本
