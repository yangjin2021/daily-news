# daily-news

一个给 ChatGPT 阅读的每日内容仓库。🌐🧠

目标不是把网页抓下来堆成垃圾，而是把网页变成可以被你和 ChatGPT 每天阅读、筛选、复盘的知识流。

## 工作流

```text
sources.yaml
    ↓
scripts/collect.py
    ↓
outputs/YYYY-MM-DD.md
    ↓
你在 ChatGPT 里说：读取我今天的 daily-news，整理成今日简报
```

## 目录

```text
sources.yaml                 # 内容来源：RSS / 网站 / GitHub / 博客
scripts/collect.py           # 采集与清洗脚本
outputs/                     # 每日生成的 Markdown 简报原料
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
```

## 自动运行

GitHub Actions 默认每天北京时间早上 7:30 左右运行一次，也可以在 GitHub 的 Actions 页面手动运行。

## 和 ChatGPT 配合

每天你可以直接在 ChatGPT 里说：

> 读取我的 daily-news 仓库，整理今天值得看的内容。

我会把 `outputs/` 里的 Markdown 变成你的每日阅读界面：摘要、分组、洞察、选题、待深挖方向。

## 下一步

后续可以继续加：

- Playwright：打开动态网页
- Scrapling：更强的页面提取
- SQLite：保存历史全文
- 向量检索：让 ChatGPT 按主题回忆旧内容
- 选题生成：把每日内容转成文章、视频、播客脚本
