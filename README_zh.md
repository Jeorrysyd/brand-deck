# BrandDeck — AI 营销 PPT 生成器

> **一句话 + 素材 → 品牌合规的 PPT，全自动。**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

## 这是什么？

一个**开源的本地工具**：用自然语言描述你要什么 → AI 理解内容并决定最佳排版 → 自动生成符合品牌规范的 `.pptx` 文件。

**这不是模板填充工具，是 AI 营销助手。**

你不需要懂 JSON、不需要选模板、不需要学排版。你只需要：

1. 🎨 一次性配好品牌信息（色板、字体、Logo）
2. 📎 把素材丢给它（文字、图片、PDF、Word、链接…任何形式）
3. 💬 说一句「帮我做成 PPT」

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
品牌 PPTX 模板 (可选): ./template.pptx
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

# 指定输出路径
brand-deck make "竞品分析汇报" --attach notes.txt -o competitor-analysis.pptx

# 交互模式：AI 先出方案，你确认后再生成
brand-deck make "年度内容策略" --interactive
# → AI: "计划做12页：封面→策略概览→三支柱→月度节奏→KPI→End Card。继续？"
# → 你: y
# → 生成 .pptx 并自动打开
```

### 在 AI 编程助手里用（Claude Code / Cursor / Floatboat）

```
你: 「帮我把 ~/scripts/ 下的拍摄脚本做成品牌PPT」
AI: 读取文件 → 调用 brand-deck make → 输出 .pptx
```

---

## 工作原理

```
  你的输入（任何形式）
  文字 / 图片 / PDF / Word / 语音转文字 / URL
                    │
                    ▼
  ┌─────────────────────────────────┐
  │  文件读取器                      │
  │  统一转换为纯文本                │
  │  支持: .docx .pdf .txt 图片     │
  └────────────────┬────────────────┘
                    │
                    ▼
  ┌─────────────────────────────────────────────────┐
  │  AI 层                                           │
  │                                                  │
  │  System Prompt = 品牌规范 + PPT设计知识库         │
  │                  + 页面类型库 + JSON Schema       │
  │                                                  │
  │  支持: Claude / Gemini（用户选择）                │
  │                                                  │
  │  输出: 结构化 JSON（逐页）                        │
  │      + 设计说明（为什么选这个版式）                │
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
  │  预览确认                        │
  │  展示大纲 → 你说OK → 开始渲染    │
  └────────────────┬────────────────┘
                    │
                    ▼
  ┌─────────────────────────────────────────────────┐
  │  渲染引擎                                        │
  │                                                  │
  │  12+ 页面类型：                                   │
  │  封面 · 章节页 · 图文并排 · 表格 · 分镜 ·        │
  │  日历 · 网格 · 图表占位 · 金句 · 对比 ·          │
  │  要点列表 · 尾页                                  │
  │                                                  │
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
| `grid` | 多图 / 多卡片网格 | 作品集、团队、功能展示 |
| `chart_placeholder` | 图表占位（后续补数据） | 数据驱动的页面 |
| `quote` | 引用 / 金句页 | 用户证言、关键洞察 |
| `comparison` | 并排对比（vs / 前后） | 竞品分析、A/B 测试 |
| `bullets` | 要点列表 + 图标 | 摘要、议程 |
| `end_card` | 尾页 + CTA | 感谢页、联系方式 |

---

## 覆盖的营销场景

### 📝 内容制作类
- **拍摄分镜脚本** — 逐镜头画面 / 运镜 / 台词 / 字卡 / 时长
- **内容日历 / 排期表** — 按周/月的发布计划，标注平台 / 类型 / 负责人
- **Social Plan** — 策略概览 + 内容支柱 + 执行节奏 + KPI

### 🏷️ 产品与品牌类
- **新品发布 Deck** — 产品亮点 + 卖点 + 目标人群 + CTA
- **品牌策略汇报** — 定位 + 调性 + 竞品 + 路线图
- **KOL/达人合作方案** — 达人清单 + 合作形式 + 预算 + 排期

### 📊 分析与汇报类
- **竞品分析** — 竞品矩阵 + SWOT + 关键洞察
- **活动复盘** — 数据总结 + 亮点 + 用户反馈 + 改进
- **月度/季度汇报** — 数据看板 + 内容表现 + 下一步

### 🎓 其他
- **团队培训 / Onboarding** — 品牌知识 + 流程 SOP
- **提案 / Pitch Deck** — 客户提案、商业方案
- **用户旅程地图** — 触点 + 痛点 + 机会点

---

## 核心设计决策

| 决策 | 为什么 |
|---|---|
| **输出 .pptx，不是 PDF/HTML** | 营销人的下游流程就是在 PowerPoint/Keynote 里微调。可编辑是刚需。 |
| **AI 决定排版，不是套模板** | 模板限制灵活性。AI 根据内容语义决定版式——这是核心价值。 |
| **JSON 作为中间格式** | 解耦 AI 决策和渲染。支持校验、预览、重试，再提交给渲染引擎。 |
| **未知页面类型自动降级** | AI 可能幻觉出不存在的类型。优雅降级为「要点列表」，永不崩溃。 |
| **JSON Schema 校验 + 自动重试** | LLM 输出天然不确定。校验层捕获格式错误、缺字段、无效类型——自动重试 2 次。 |
| **预览-确认-生成** | 减少「生成了但不是我要的」的浪费。AI 先展示大纲，你确认了再渲染。 |
| **AI 决策透明度** | AI 解释每一页为什么选这个版式。建立信任，方便迭代。 |

---

## 错误处理

BrandDeck 的设计原则是**零静默失败**——任何问题都会给你清晰的提示，而不是默默出错。

| 问题 | 处理方式 |
|---|---|
| AI 调用超时 | 指数退避重试（最多 3 次） |
| AI 返回限流 (429) | 等待 + 重试 |
| API Key 无效 | 明确提示：「请检查 brand.yaml 中的 API Key」 |
| AI 输出格式错误 | 自动重试（最多 2 次），带更严格的提示 |
| AI 输出未知页面类型 | 自动降级为「要点列表」渲染器 |
| 不支持的文件格式 | 明确列出支持的格式 |
| 字体未安装 | 降级为系统字体 + 警告提示 |
| 图片找不到 | 使用占位符 + 提示 |

---

## 安全说明

| 关注点 | 处理方式 |
|---|---|
| API Key 安全 | 仅存储在本地 `brand.yaml`，`.gitignore` 模板默认排除。CLI 会在你试图提交时警告。 |
| 输入内容安全 | AI 输出是结构化 JSON，渲染器只读取白名单字段，不执行任何代码。 |
| 文件输入安全 | 使用成熟库（python-docx, pdfplumber），仅提取文本，无 eval/exec。 |
| 依赖安全 | 最小化依赖，全部在 `pyproject.toml` 中锁定版本。 |

---

## 项目结构

```
brand-deck/
├── README.md                     # English version
├── README_zh.md                  # 中文版（本文件）
├── LICENSE                       # MIT
├── pyproject.toml                # 依赖管理
│
├── src/brand_deck/
│   ├── cli.py                    # 命令行入口：init / make / preview
│   ├── ai.py                     # AI 层：Claude/Gemini 后端
│   ├── validator.py              # JSON Schema 校验 + 重试逻辑
│   ├── builder.py                # 渲染编排：JSON → PPTX
│   ├── theme.py                  # 品牌主题：brand.yaml → 颜色/字体对象
│   ├── renderers/                # 12+ 页面类型渲染器
│   │   ├── __init__.py           # 渲染器注册 + 降级逻辑
│   │   ├── base.py               # 基础渲染器抽象类
│   │   ├── cover.py              # 全幅封面
│   │   ├── section.py            # 章节分隔页
│   │   ├── text_image.py         # 图文并排
│   │   ├── table.py              # 数据表格
│   │   ├── storyboard.py         # 分镜表格
│   │   ├── calendar.py           # 日历/时间线
│   │   ├── grid.py               # 多图/卡片网格
│   │   ├── chart_placeholder.py  # 图表占位
│   │   ├── quote.py              # 引用/金句
│   │   ├── comparison.py         # 对比页
│   │   ├── bullets.py            # 要点列表（也是降级目标）
│   │   └── end_card.py           # 尾页
│   ├── utils/
│   │   ├── pptx_helpers.py       # 底层 PPT 操作函数
│   │   └── file_reader.py        # 读取各种输入格式 → 文本
│   └── prompts/
│       └── system.py             # 动态生成 System Prompt
│
├── brands/
│   ├── _template.yaml            # 空白品牌模板
│   └── therabody.yaml            # 示例品牌配置
│
├── examples/                     # 各场景示例
│   ├── shooting-script/
│   ├── content-calendar/
│   ├── product-launch/
│   └── social-plan/
│
├── docs/                         # 详细文档
│   ├── getting-started.md
│   ├── use-cases.md
│   ├── brand-config.md
│   ├── for-developers.md
│   └── prompt-engineering.md
│
└── tests/                        # 测试
```

---

## 实现路线图

### Phase 1：核心可用 — "端到端跑通"

1. 项目结构 + 依赖管理
2. 品牌配置加载（`brand.yaml` → `BrandTheme`）
3. 文件读取器（.docx / .pdf / .txt → 纯文本）
4. 从已有代码提取 → PPT 基础操作函数
5. 6 个核心渲染器：封面、图文并排、表格、分镜、要点列表、尾页
6. 渲染编排引擎 + 降级逻辑
7. AI 层 + System Prompt 动态生成
8. JSON Schema 校验 + 自动重试
9. CLI：`brand-deck init` + `brand-deck make` + 预览确认
10. 生成后自动打开 + AI 设计说明输出
11. Therabody 品牌端到端验证

### Phase 2：丰富场景

12. 补全剩余渲染器：章节页、日历、网格、金句、对比、图表占位
13. Gemini 后端
14. 更多示例
15. 完整版交互模式

### Phase 3：开源发布

16. README（中英双语）+ 文档
17. PyPI 发布（`pip install brand-deck`）
18. GitHub Actions CI
19. 示例截图 + Demo GIF
20. AOE Combo 封装（Floatboat 集成）

---

## AI 服务说明

BrandDeck 支持多个 AI 后端：

| AI 服务 | 配置方式 | 说明 |
|---|---|---|
| **Claude** (Anthropic) | `ai: claude` | 推荐。对中文和英文理解都很好。 |
| **Gemini** (Google) | `ai: gemini` | 备选。 |
| **DeepSeek** | `ai: deepseek` | 国内友好，无需代理。（规划中） |

在 `brand.yaml` 中设置 `ai: claude`，或通过环境变量 `BRANDDECK_AI=gemini`。

> **💡 关于国内使用**：Claude 和 Gemini 在国内需要代理。如果你在国内使用，可以：
> 1. 配置系统代理
> 2. 等待 DeepSeek 后端支持（Phase 2 规划中）
> 3. 使用兼容 OpenAI API 格式的国内服务（通过环境变量配置 base URL）

---

## 长期愿景

```
  现在                        v1（本项目）                   未来（v2+）
  ┌──────────────┐    ┌─────────────────────┐    ┌───────────────────────────┐
  │ 单品牌定制脚本 │ →  │ 通用品牌 PPT 生成器  │ →  │ 营销团队 AI 内容平台        │
  │ 只能做一种PPT  │    │ 12+ 页面类型         │    │ - 多品牌管理               │
  │ 硬编码品牌色   │    │ 任意营销场景          │    │ - 团队共享（brand.yaml）   │
  │ 没有AI排版    │    │ AI 智能排版决策       │    │ - Web UI + API             │
  └──────────────┘    │ 品牌配置化            │    │ - 插件市场（自定义渲染器） │
                      └─────────────────────┘    │ - 多格式输出               │
                                                  │  （PPT / PDF / 社交卡片）  │
                                                  └───────────────────────────┘
```

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
