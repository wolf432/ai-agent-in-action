# AI Agent in Action 🛠️

《老兵学 Agent》系列文章配套代码。10 年后端转向 AI 应用开发,按真实踩坑顺序记录,不写教程,只写工程视角的实战。

## 文章目录

| # | 文章 | 代码 |
|---|------|------|
| 01 | 同一段 tool calling 代码,DeepSeek 报错,GLM 却"正常" | [01-tool-calling](./01-tool-calling) |

## 运行

```bash
uv sync
cp .env.example .env  # 填入你的 API_KEY / BASE_URL / MODEL
uv run 01-tool-calling/robust_tool_calling.py
```

## 关注公众号

系列文章首发于公众号,踩坑实录 + 架构思考,每周更新:

<!-- TODO: 替换为公众号二维码 -->
![公众号二维码](./assets/qrcode.jpg)

觉得有用请点个 ⭐ Star,这是我持续更新的最大动力。
