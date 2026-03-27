<div align="center">

# BrandDeck

**Natural language + attachments → brand-compliant `.pptx` — fully automated**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

<br>

**Language / 语言**
[🇺🇸 English](#english) · [🇨🇳 中文](#中文)

</div>

---

<a name="english"></a>

<details open>
<summary><strong>🇺🇸 English</strong></summary>

<br>

## What is BrandDeck?

An open-source, local-first CLI tool: describe what you need in natural language → AI understands your content and decides the optimal layout → automatically generates a brand-compliant `.pptx`.

**This is not a template-filling tool. It's an AI marketing assistant.**

Users don't need to know JSON, pick templates, or learn layout design. They just need to:

1. Configure brand info once (color palette, fonts, logo)
2. Throw materials at the AI (text, images, PDF, links… any format)
3. Say "make it a PPT"

---

## Two Usage Modes

### 🤖 Agent Mode — No API Key Needed (Recommended)

Use BrandDeck inside **Claude Code**, **Floatboat**, **Cursor**, or any AI agent with a subscription. The agent generates the slide structure; BrandDeck handles the rendering.

```bash
# Step 1: Set up brand (skip API key)
brand-deck init --agent

# Step 2: Ask your agent to generate slides JSON, then render:
brand-deck render slides.json

# Or pipe JSON directly from agent output:
brand-deck render '{"slides": [{"type": "cover", "title": "My Deck"}, ...]}'

# See the JSON schema:
brand-deck schema
```

**In Claude Code / Floatboat**, just say:
```
"Turn this brief into a PPT using brand-deck"
→ Agent reads files → generates slide JSON → calls brand-deck render → opens .pptx
```

### 🔑 Standalone Mode — With API Key

Use BrandDeck as a standalone CLI with your own Claude/Gemini API key.

```bash
brand-deck init       # set up brand + API key
brand-deck make "Turn this shooting script into a storyboard PPT" --attach script.docx
```

---

## Core Philosophy

**"Any marketing content → Brand PPT"**

| You say… | AI does… |
|---|---|
| "Turn this shooting script into a storyboard PPT" | Auto-detects Storyboard format, generates shot tables + scene descriptions |
| "Make a Xiaohongshu content calendar for next month" | Calendar table + content type labels + timeline |
| "Turn this Social Plan into a presentation deck" | Strategy overview + content pillars + execution plan + KPI targets |
| "New product launch deck" | Product highlights + key selling points + competitive comparison + CTA |
| "Competitive analysis PPT for the boss" | Competitor matrix + SWOT + key findings + recommendations |
| "Post-campaign recap report" | Data summary + highlights + user feedback + next steps |
| "KOL collaboration proposal" | KOL roster + collaboration format + budget + timeline |
| "Annual brand content strategy" | Strategy framework + three pillars + monthly cadence + KPI |

**AI doesn't fill templates — it decides which page combinations, layouts, and compositions to use based on content semantics.**

---

## Quick Start

### Install

```bash
pip install brand-deck
```

### Initialize Brand (one-time)

```bash
brand-deck init
```

Interactive setup:
```
Brand name: Therabody
Primary color (hex): #000000
Accent color (hex): #F5A37F
Background color (hex): #D1D3CD
Heading font: TT Norms Medium
Body font: TT Norms Regular
Logo file path (optional): ./logo.png
AI service: claude  (options: gemini)
API Key: sk-...

→ Saved: brand.yaml
```

### Daily Usage

```bash
# Simplest: one sentence + attachments
brand-deck make "Turn this shooting script into a storyboard PPT" \
  --attach script.docx --attach ./images/

# From file
brand-deck make "Make a product launch deck" --attach product-brief.pdf

# Pure text input
brand-deck make "Make a March Xiaohongshu content calendar, 4 posts per week, covering running, tennis, yoga scenarios"

# Interactive mode: AI proposes plan, you confirm, then it generates
brand-deck make "Annual content strategy" --interactive
# → AI: "I plan to create 12 slides: Cover → Strategy Overview → Three Pillars → Monthly Cadence → KPI → End Card. Proceed?"
# → You: y
# → Generates .pptx
```

### Use with AI Coding Assistants (Claude Code / Cursor / Floatboat)

```
You: "Turn the shooting scripts in ~/scripts/ into a brand PPT"
AI: reads files → calls brand-deck make → outputs .pptx
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  USER INPUT                                              │
│  text / .docx / .pdf / .txt / images / URL / transcript  │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────┐
│  FILE READER (file_reader.py)        │
│  Normalizes all input → plain text   │
│  Supports: .docx .pdf .txt images    │
└────────────────────────┬────────────┘
                         │ (normalized text)
                         ▼
┌─────────────────────────────────────────────────────────┐
│  AI LAYER (ai.py)                                        │
│  System Prompt = Brand Config + Design Knowledge         │
│                + Page Type Library + JSON Schema         │
│  ┌──────────────┐  ┌──────────────┐                     │
│  │ClaudeBackend │  │GeminiBackend │  (user chooses)      │
│  └──────────────┘  └──────────────┘                     │
│  Output: Structured JSON + Design Reasoning per slide    │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────┐
│  JSON VALIDATOR (validator.py)       │
│  jsonschema validation + auto-retry  │
│  (max 2 retries on malformed output) │
└────────────────────────┬────────────┘
                         │
                         ▼
┌─────────────────────────────────────┐
│  PREVIEW (cli.py --interactive)      │
│  Shows outline → user confirms → go  │
└────────────────────────┬────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  RENDER ENGINE (builder.py)                              │
│  Renderer Registry (12+ page types):                     │
│  cover · section · text_image · table · storyboard ·     │
│  calendar · grid · chart_placeholder · quote ·            │
│  comparison · bullets · end_card                          │
│  Fallback: unknown page types → bullets (never crashes)   │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
                   brand.pptx ✅ → auto-opens
```

---

## Page Type Library

AI freely combines these 12+ page types based on content:

| Type | Description | Best For |
|---|---|---|
| `cover` | Full-bleed image cover with overlay + title | Opening slide |
| `section` | Chapter divider page | Separating major sections |
| `text_image` | Side-by-side text + image (left/right variants) | Product features, case studies |
| `table` | Data table with branded styling | Schedules, comparisons, specs |
| `storyboard` | Shot-by-shot table with scene descriptions | Video production scripts |
| `calendar` | Calendar/timeline layout | Content calendars, schedules |
| `grid` | Multi-image or multi-card grid | Portfolio, team, features |
| `chart_placeholder` | Chart placeholder (user adds data later) | Data-driven slides |
| `quote` | Pull quote / key message page | Testimonials, key takeaways |
| `comparison` | Side-by-side comparison (vs / before-after) | Competitive analysis, A/B |
| `bullets` | Key points list with icons | Summaries, agendas, lists |
| `end_card` | Closing page with CTA | Thank you, contact info |

---

## Marketing Scenarios (Out of the Box)

**Content Production**
- Shooting Script / Storyboard — shot-by-shot visuals / camera / dialogue / duration
- Content Calendar — weekly/monthly publishing plan with platform, type, owner labels
- Social Plan — strategy overview + content pillars + execution cadence + KPI

**Product & Brand**
- Product Launch Deck — highlights + selling points + target audience + CTA
- Brand Strategy Report — positioning + tone + competitive landscape + roadmap
- KOL/Influencer Proposal — influencer roster + collaboration format + budget + timeline

**Analysis & Reporting**
- Competitive Analysis — competitor matrix + SWOT + key insights
- Campaign Recap — data summary + highlights + user feedback + improvements
- Monthly/Quarterly Report — data dashboard + content performance + next steps

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| **Output is .pptx, not PDF/HTML** | Marketing teams' downstream workflow is editing in PowerPoint/Keynote. Editable output is essential. |
| **AI-first rendering, not template-filling** | Templates limit flexibility. AI decides layout based on content semantics — the core value proposition. |
| **JSON as intermediate format** | Decouples AI decisions from rendering. Enables validation, preview, and retry before committing to PPTX generation. |
| **Fallback renderer for unknown types** | AI may hallucinate page types. Graceful degradation to `bullets` instead of crashing. |
| **JSON Schema validation + 2x retry** | LLM output is non-deterministic. Validation layer catches malformed JSON, retries automatically. |
| **Preview-confirm-generate flow** | Reduces wasted renders. AI shows outline first, user confirms, then renders. |
| **Design reasoning in output** | AI explains why it chose each page type. Builds user trust and enables iterative refinement. |

---

## Project Structure

```
brand-deck/
├── README.md
├── LICENSE                       # MIT
├── pyproject.toml                # Deps: python-pptx, click, anthropic, jsonschema...
├── src/brand_deck/
│   ├── cli.py                    # CLI: init / make / preview
│   ├── ai.py                     # AI layer: Claude/Gemini backends
│   ├── validator.py              # JSON Schema validation + retry logic
│   ├── builder.py                # DeckBuilder: JSON → PPTX orchestration
│   ├── theme.py                  # BrandTheme: brand.yaml → color/font objects
│   ├── renderers/                # 12+ page type renderers
│   ├── utils/
│   │   ├── pptx_helpers.py       # Low-level python-pptx operations
│   │   └── file_reader.py        # Read .docx/.pdf/.txt → text
│   └── prompts/
│       └── system.py             # Dynamic system prompt (injects brand config)
├── brands/
│   ├── _template.yaml            # Blank brand template
│   └── therabody.yaml            # Example brand config
└── examples/                     # Example inputs + outputs per scenario
```

---

## Error Handling

BrandDeck is designed for **zero silent failures**:

| Problem | Handling |
|---|---|
| AI API timeout | Retry with exponential backoff (max 3×) |
| Rate limited (429) | Wait + retry |
| Invalid API key | Clear error: "Check your API key in brand.yaml" |
| Malformed AI output | Auto-retry (max 2×) with stricter prompt |
| Unknown page type | Fallback to `bullets` renderer |
| Unsupported file format | Clear error listing supported formats |
| Font not installed | Fallback to system fonts + warning |
| Image not found | Placeholder with "[Image not found]" text |

---

## Contributing

We welcome contributions! See `docs/for-developers.md` for:
- How to add a new page type renderer
- How to add a new AI backend
- How to customize the system prompt
- Testing guidelines

---

## License

MIT — see [LICENSE](LICENSE) for details.

</details>

---

<a name="中文"></a>

<details>
<summary><strong>🇨🇳 中文</strong></summary>

<br>

## 这是什么？

一个**开源的本地工具**：用自然语言描述你要什么 → AI 理解内容并决定最佳排版 → 自动生成符合品牌规范的 `.pptx` 文件。

**这不是模板填充工具，是 AI 营销助手。**

你不需要懂 JSON、不需要选模板、不需要学排版。你只需要：

1. 🎨 一次性配好品牌信息（色板、字体、Logo）
2. 📎 把素材丢给它（文字、图片、PDF、Word、链接…任何形式）
3. 💬 说一句「帮我做成 PPT」

---

## 两种使用方式

### 🤖 Agent 模式 — 无需 API Key（推荐）

在 **Claude Code**、**Floatboat**、**Cursor** 等 AI Agent 中使用。Agent 负责生成幻灯片结构，BrandDeck 只负责渲染 PPTX。

```bash
# 第一步：初始化品牌（跳过 API Key）
brand-deck init --agent

# 第二步：让 Agent 生成 JSON，然后渲染：
brand-deck render slides.json

# 或者直接管道传入 JSON：
brand-deck render '{"slides": [{"type": "cover", "title": "我的PPT"}, ...]}'

# 查看 JSON Schema：
brand-deck schema
```

**在 Claude Code / Floatboat 里**，直接说：
```
「把这个 brief 做成 PPT，用 brand-deck 渲染」
→ Agent 读取文件 → 生成 slides JSON → 调用 brand-deck render → 打开 .pptx
```

### 🔑 独立模式 — 配置 API Key

用你自己的 Claude/Gemini API Key，brand-deck 独立调用 AI。

```bash
brand-deck init       # 配置品牌 + API Key
brand-deck make "把这个拍摄脚本做成分镜PPT" --attach script.docx
```

---

## 为什么做这个？

每个营销人都经历过：

- 老板说「明天要一个 deck」→ 你熬夜到凌晨调排版
- 找了半天模板 → 填完内容发现根本不对
- 做完了 → 品牌部说配色不对、字体不对、Logo 位置不对
- 竞品分析 / 内容日历 / 拍摄脚本 → 每次都从零开始做 PPT

**BrandDeck 解决的问题很简单：把你从排版的地狱里解放出来。**

AI 不是套模板——它根据你的内容语义，自动决定用什么页面组合、什么版式、怎么排。你配好一次品牌信息，以后所有 PPT 都自动合规。

---

## 它能做什么？

| 你说… | AI 做… |
|---|---|
| 「把这个拍摄脚本做成分镜 PPT」 | 自动识别为 Storyboard，生成分镜表格 + 场景描述 |
| 「做一个下个月的小红书内容日历」 | 日历表格 + 内容类型标注 + 时间线 |
| 「把这份 Social Plan 做成汇报用的 deck」 | 策略概览 + 内容支柱 + 执行计划 + 数据目标 |
| 「新品上市的产品发布 deck」 | 产品亮点 + 核心卖点 + 竞品对比 + CTA |
| 「竞品分析做成 PPT 给老板看」 | 竞品矩阵 + SWOT + 关键发现 + 建议 |
| 「这次活动的复盘报告」 | 数据总结 + 亮点回顾 + 用户反馈 + 下一步 |
| 「KOL 合作方案」 | KOL 清单 + 合作形式 + 预算 + 时间线 |
| 「品牌年度内容策略」 | 策略框架 + 三支柱 + 月度节奏 + KPI |

**AI 不受限于这个列表** — 你可以描述任何场景，它会自主判断最佳的页面组合。

---

## 适合谁用？

- 🎯 **品牌方营销团队** — 做 social plan、内容日历、竞品分析、活动方案
- 🎬 **内容制作团队** — 拍摄脚本转分镜、KOL 合作方案
- 📊 **市场分析师** — 竞品研究、月度/季度汇报
- 🏢 **Agency / 乙方** — 客户提案、pitch deck、活动复盘
- 🌍 **中文 / 英文 / 多语言团队** — AI 支持任何语言，品牌配置通用

**没有地域限制。** 中国团队、海外团队、跨国品牌都能用。

---

## 快速上手

### 安装

```bash
pip install brand-deck
```

### 初始化品牌（只需一次）

```bash
brand-deck init
```

按引导填写：
```
品牌名称: Therabody
主色 (hex): #000000
强调色 (hex): #F5A37F
背景色 (hex): #D1D3CD
标题字体: TT Norms Medium
正文字体: TT Norms Regular
Logo 文件路径 (可选): ./logo.png
AI 服务: claude  (可选: gemini / deepseek)
API Key: sk-...

→ 已保存: brand.yaml
```

### 日常使用

```bash
# 最简单的用法：一句话 + 附件
brand-deck make "把这个拍摄脚本做成分镜PPT" --attach script.docx --attach ./images/

# 从文件生成
brand-deck make "做成产品发布deck" --attach product-brief.pdf

# 纯文字输入
brand-deck make "做一个3月份的小红书内容日历，每周4条，覆盖跑步、网球、瑜伽场景"

# 交互模式：AI 先出方案，你确认后再生成
brand-deck make "年度内容策略" --interactive
# → AI: "计划做12页：封面→策略概览→三支柱→月度节奏→KPI→End Card。继续？"
# → 你: y
# → 生成 .pptx 并自动打开
```

### 在 AI 助手里用（Claude Code / Cursor / Floatboat）

```
你: 「帮我把 ~/scripts/ 下的拍摄脚本做成品牌PPT」
AI: 读取文件 → 调用 brand-deck make → 输出 .pptx
```

---

## 工作原理

```
  你的输入（任何形式）
  文字 / 图片 / PDF / Word / URL
                │
                ▼
  ┌─────────────────────────────────┐
  │  文件读取器                      │
  │  统一转换为纯文本                │
  └────────────────┬────────────────┘
                   │
                   ▼
  ┌─────────────────────────────────────────────────┐
  │  AI 层                                           │
  │  System Prompt = 品牌规范 + PPT设计知识           │
  │                + 页面类型库 + JSON Schema         │
  │  支持: Claude / Gemini（用户选择）                │
  │  输出: 结构化 JSON + 每页设计说明                  │
  └────────────────┬────────────────────────────────┘
                   │
                   ▼
  ┌─────────────────────────────────┐
  │  JSON 校验器                     │
  │  Schema 校验 + 自动重试（最多2次）│
  └────────────────┬────────────────┘
                   │
                   ▼
  ┌─────────────────────────────────┐
  │  预览确认（--interactive 模式）   │
  │  展示大纲 → 你说OK → 开始渲染    │
  └────────────────┬────────────────┘
                   │
                   ▼
  ┌─────────────────────────────────────────────────┐
  │  渲染引擎                                        │
  │  12+ 页面类型：封面 · 章节页 · 图文并排 · 表格    │
  │  分镜 · 日历 · 网格 · 金句 · 对比 · 要点列表 · 尾页│
  │  遇到未知类型 → 降级为要点列表（永不崩溃）         │
  └────────────────┬────────────────────────────────┘
                   │
                   ▼
             品牌PPT.pptx ✅ → 自动打开
```

---

## 页面类型库

AI 根据内容自由组合这 12+ 种页面类型：

| 类型 | 说明 | 适合场景 |
|---|---|---|
| `cover` | 全幅图封面 + 遮罩 + 标题 | 开场 |
| `section` | 章节分隔页 | 分大章节 |
| `text_image` | 图文并排（左图右文 / 右图左文） | 产品特性、案例 |
| `table` | 品牌风格数据表格 | 排期表、规格对比 |
| `storyboard` | 逐镜头分镜表格 | 视频拍摄脚本 |
| `calendar` | 日历 / 时间线 | 内容日历、排期 |
| `grid` | 多图 / 多卡片网格 | 作品集、团队展示 |
| `chart_placeholder` | 图表占位（后续补数据） | 数据驱动的页面 |
| `quote` | 引用 / 金句页 | 用户证言、关键洞察 |
| `comparison` | 并排对比（vs / 前后） | 竞品分析、A/B 测试 |
| `bullets` | 要点列表 + 图标 | 摘要、议程 |
| `end_card` | 尾页 + CTA | 感谢页、联系方式 |

---

## 覆盖的营销场景

**📝 内容制作类**
- 拍摄分镜脚本 — 逐镜头画面 / 运镜 / 台词 / 时长
- 内容日历 / 排期表 — 按周/月的发布计划
- Social Plan — 策略概览 + 内容支柱 + 执行节奏 + KPI

**🏷️ 产品与品牌类**
- 新品发布 Deck — 产品亮点 + 卖点 + 目标人群 + CTA
- 品牌策略汇报 — 定位 + 调性 + 竞品 + 路线图
- KOL/达人合作方案 — 达人清单 + 合作形式 + 预算 + 排期

**📊 分析与汇报类**
- 竞品分析 — 竞品矩阵 + SWOT + 关键洞察
- 活动复盘 — 数据总结 + 亮点 + 用户反馈 + 改进
- 月度/季度汇报 — 数据看板 + 内容表现 + 下一步

---

## 核心设计决策

| 决策 | 为什么 |
|---|---|
| **输出 .pptx，不是 PDF/HTML** | 营销人的下游流程就是在 PowerPoint/Keynote 里微调。可编辑是刚需。 |
| **AI 决定排版，不是套模板** | 模板限制灵活性。AI 根据内容语义决定版式——这是核心价值。 |
| **JSON 作为中间格式** | 解耦 AI 决策和渲染。支持校验、预览、重试，再提交给渲染引擎。 |
| **未知页面类型自动降级** | AI 可能幻觉出不存在的类型。优雅降级为「要点列表」，永不崩溃。 |
| **JSON Schema 校验 + 自动重试** | LLM 输出天然不确定。自动重试 2 次，捕获格式错误。 |
| **预览-确认-生成** | 减少「生成了但不是我要的」的浪费。AI 先展示大纲，你确认了再渲染。 |
| **AI 决策透明度** | AI 解释每一页为什么选这个版式。建立信任，方便迭代。 |

---

## AI 服务说明

| AI 服务 | 配置 | 说明 |
|---|---|---|
| **Claude** (Anthropic) | `ai: claude` | 推荐。中英文理解都很好。 |
| **Gemini** (Google) | `ai: gemini` | 备选。 |
| **DeepSeek** | `ai: deepseek` | 国内友好，无需代理。（规划中） |

> **💡 国内使用提示**：Claude 和 Gemini 在国内需要代理。可配置系统代理，或等待 DeepSeek 后端支持（Phase 2 规划中）。

---

## 错误处理

| 问题 | 处理方式 |
|---|---|
| AI 调用超时 | 指数退避重试（最多 3 次） |
| AI 返回限流 (429) | 等待 + 重试 |
| API Key 无效 | 明确提示：「请检查 brand.yaml 中的 API Key」 |
| AI 输出格式错误 | 自动重试（最多 2 次） |
| AI 输出未知页面类型 | 自动降级为「要点列表」渲染器 |
| 不支持的文件格式 | 明确列出支持的格式 |
| 字体未安装 | 降级为系统字体 + 警告提示 |
| 图片找不到 | 使用占位符 + 提示 |

---

## 参与贡献

欢迎贡献代码！详见 `docs/for-developers.md`：
- 如何添加新的页面类型渲染器
- 如何添加新的 AI 后端
- 如何自定义 System Prompt
- 测试指南

---

## 开源协议

MIT — 详见 [LICENSE](LICENSE)

</details>
