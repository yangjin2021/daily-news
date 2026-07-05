# AGENTS.md

这个仓库是一个 GPT 可调用的信息采集与报告工具。

当用户要求“查一下 / 采集 / 出报告 / 今日有什么 / 帮我看某个方向”时，不要只读旧文件，优先运行：

```bash
python scripts/report.py --query "<用户主题>" --max-items 12 --depth standard --print
```

如果用户要快一点，或者已经确认只看缓存：

```bash
python scripts/report.py --query "<用户主题>" --from-cache --print
```

输出文件位置：

- `reports/YYYY-MM-DD-<topic>.md`：给人和 GPT 读的报告
- `reports/latest-report.json`：结构化结果
- `outputs/YYYY-MM-DD.md`：全量每日原料
- `site/data/news.json`：网页数据

使用规则：

- 主题明确时直接运行，不要反复问。
- 主题很宽时默认 `--max-items 12 --depth standard`。
- 用户要深挖时用 `--depth deep`。
- 用户要简报时用 `--depth brief`。
- 运行后把报告里的关键结论直接回复给用户，并给出报告文件路径。
