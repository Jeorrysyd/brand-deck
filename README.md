# BrandDeck — AI-Powered Marketing PPT Generator

> **Turn any marketing content into a brand-compliant PPTX — with one command.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

## What is BrandDeck?

An open-source, local-first CLI tool: describe what you need in natural language → AI understands your content and decides the optimal layout → automatically generates a brand-compliant `.pptx`.

**This is not a template-filling tool. It's an AI marketing assistant.**

Users don't need to know JSON, pick templates, or learn layout design. They just need to:

1. Configure brand info once (color palette, fonts, logo)
2. Throw materials at the AI (text, images, PDF, links… any format)
3. Say "make it a PPT"

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
Brand PPTX template (optional): ./template.pptx
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

# Specify output
brand-deck make "Competitive analysis report" --attach notes.txt -o competitor-analysis.pptx

# Interactive mode: AI proposes plan, you confirm, then it generates
brand-deck make "Annual content strategy" --interactive
# → AI: "I plan to create 12 slides: Cover → Strategy Overview → Three Pillars → Monthly Cadence → KPI → End Card. Proceed?"
# → You: y
# → Generates .pptx
```

### Use with AI Coding Assistants (Claude Code / Cursor)

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
│                                                          │
│  System Prompt = Brand Config + Design Knowledge         │
│                  + Page Type Library + JSON Schema        │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐                     │
│  │ClaudeBackend │  │GeminiBackend │  (user chooses)      │
│  └──────────────┘  └──────────────┘                     │
│                                                          │
│  Output: Structured JSON (slide-by-slide)                │
│        + Design Reasoning (why each page type was chosen)│
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
                         │ (confirmed JSON)
                         ▼
┌─────────────────────────────────────────────────────────┐
│  RENDER ENGINE (builder.py)                              │
│                                                          │
│  Renderer Registry (12+ page types):                     │
│  cover · section · text_image · table · storyboard ·     │
│  calendar · grid · chart_placeholder · quote ·            │
│  comparison · bullets · end_card                          │
│                                                          │
│  Fallback: unknown page types → bullets (never crashes)   │
│                                                          │
│  ┌──────────────┐  ┌──────────────────┐                 │
│  │  theme.py     │  │ pptx_helpers.py  │                 │
│  │ (BrandTheme)  │  │ (low-level ops)  │                 │
│  └──────────────┘  └──────────────────┘                 │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
                   brand.pptx ✅ → auto-opens
```

### Key Design Decisions

| Decision | Rationale |
|---|---|
| **Output is .pptx, not PDF/HTML** | Marketing teams' downstream workflow is editing in PowerPoint/Keynote. Editable output is essential. |
| **AI-first rendering, not template-filling** | Templates limit flexibility. AI decides layout based on content semantics — the core value proposition. |
| **JSON as intermediate format** | Decouples AI decisions from rendering. Enables validation, preview, and retry before committing to PPTX generation. |
| **Fallback renderer for unknown types** | AI may hallucinate page types not in the registry. Graceful degradation to `bullets` instead of crashing. |
| **JSON Schema validation + 2x retry** | LLM output is inherently non-deterministic. Validation layer catches malformed JSON, missing fields, invalid types — retries automatically before surfacing errors. |
| **Preview-confirm-generate flow** | Reduces "generated but not what I wanted" waste. AI shows outline first, user confirms, then renders. |
| **Design reasoning in output** | AI explains why it chose each page type (e.g., "Page 3 uses storyboard because shooting script content was detected"). Builds user trust and enables iterative refinement. |

---

## The System Prompt — Core Asset

This is the most important asset of the entire tool. It's not a simple "please output JSON" — it's a complete **PPT design knowledge base + brand specification + output format**.

This prompt teaches any LLM:

1. **PPT Design Principles** — one core message per slide, visual hierarchy, whitespace, contrast
2. **Page Type Library** — 12+ page types, when to use each, how to combine them
3. **Brand Specification** — dynamically injected from `brand.yaml` (color palette, fonts, tone)
4. **Output Format** — unified JSON schema consumed directly by the render engine
5. **Layout Decision Logic** — too much content → split pages; has data → use table; has comparison → use dual column

```python
# prompts/system.py — Dynamic system prompt generation

SYSTEM_PROMPT_TEMPLATE = """
You are a professional marketing PPT designer.

## Brand Specification (injected from brand.yaml)
- Brand name: {name}
- Primary: {primary} / Accent: {accent} / Background: {bg}
- Heading font: {heading_font} / Body font: {body_font}
- Brand tone: {tone} (e.g., restrained, premium, resonant)

## Design Principles
1. One core message per slide
2. Visual hierarchy: title > subtitle > body > notes
3. Generous whitespace — never cram content
4. Image ratio ≥ 40% (when images available)
5. Table data: compact but readable
6. Color-block backgrounds create rhythm (dark → light → dark alternation)

## Available Page Types
{page_type_library}

## Your Workflow
1. Analyze user content, identify what type of marketing material this is
2. Decide total page count and type for each page
3. Extract and restructure content to fit each page's information capacity
4. Output JSON with design reasoning for each page

## Output Format
{json_schema}
"""
```

This prompt works with Claude, Gemini, and can be pasted into ChatGPT by users.

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

**AI is not limited to this list** — users can describe any scenario, and AI will autonomously determine the best page type combination.

---

## Marketing Scenarios (Out of the Box)

### Content Production
- **Shooting Script / Storyboard** — shot-by-shot visuals / camera movement / dialogue / text cards / duration
- **Content Calendar** — weekly/monthly publishing plan with platform, type, and owner labels
- **Social Plan** — strategy overview + content pillars + execution cadence + KPI

### Product & Brand
- **Product Launch Deck** — product highlights + selling points + target audience + CTA
- **Brand Strategy Report** — positioning + tone + competitive landscape + roadmap
- **KOL/Influencer Collaboration Proposal** — influencer roster + collaboration format + budget + timeline

### Analysis & Reporting
- **Competitive Analysis** — competitor matrix + SWOT + key insights
- **Campaign Recap** — data summary + highlights + user feedback + improvements
- **Monthly/Quarterly Report** — data dashboard + content performance + next steps

### Other
- **Team Training / Onboarding** — brand knowledge + process SOP
- **Pitch Deck** — client-facing proposals
- **User Journey Map** — touchpoints + pain points + opportunity areas

---

## Error Handling & Reliability

BrandDeck is designed for **zero silent failures**:

```
┌──────────────────────────────────────────────────────────────────────┐
│                     ERROR HANDLING FLOW                                │
│                                                                       │
│  AI Call Failed?                                                      │
│  ├─ API timeout → retry with exponential backoff (max 3x)            │
│  ├─ Rate limited (429) → wait + retry                                │
│  ├─ Auth failure → clear error: "Check your API key in brand.yaml"   │
│  └─ Network error → clear error with troubleshooting steps           │
│                                                                       │
│  AI Output Invalid?                                                   │
│  ├─ Malformed JSON → auto-retry (max 2x) with stricter prompt       │
│  ├─ Missing required fields → auto-retry with field checklist        │
│  ├─ Unknown page type → fallback to 'bullets' renderer               │
│  └─ Empty response / refusal → clear error + suggestion to rephrase  │
│                                                                       │
│  File Input Failed?                                                   │
│  ├─ Unsupported format → clear error listing supported formats       │
│  ├─ File too large → clear error with size limit info                │
│  ├─ Corrupted file → clear error + suggestion to re-export           │
│  └─ Encoding issue → attempt UTF-8/Latin-1 fallback, then error     │
│                                                                       │
│  Rendering Failed?                                                    │
│  ├─ Image not found → placeholder with "[Image not found]" text      │
│  ├─ Font not installed → fallback to system fonts, warn user         │
│  └─ PPTX write error → clear error with permissions check            │
└──────────────────────────────────────────────────────────────────────┘
```

### Security Considerations

| Threat | Mitigation |
|---|---|
| API key exposure | Stored in local `brand.yaml` only. `.gitignore` template includes `brand.yaml`. CLI warns if committing. |
| LLM prompt injection via user content | AI output is structured JSON consumed by renderer — no code execution. Renderer only reads whitelisted fields. |
| Malicious file input (crafted PDF/DOCX) | Uses well-maintained libraries (python-docx, pdfplumber) with no eval/exec. File reader extracts text only. |
| Path traversal in `--attach` | Resolved to absolute path, validated to exist. No symlink following. |
| Dependency supply chain | Minimal dependencies. All pinned in `pyproject.toml`. |

---

## Project Structure

```
brand-deck/
├── README.md                     # English (this file)
├── README_zh.md                  # 中文详细版
├── LICENSE                       # MIT
├── pyproject.toml                # Deps: python-pptx, pyyaml, click, Pillow,
│                                 #       anthropic/google-genai, jsonschema,
│                                 #       python-docx, pdfplumber
│
├── src/brand_deck/
│   ├── __init__.py
│   ├── cli.py                    # CLI: init / make / preview
│   ├── ai.py                     # AI layer: Claude/Gemini backends
│   ├── validator.py              # JSON Schema validation + retry logic
│   ├── builder.py                # DeckBuilder: JSON → PPTX orchestration
│   ├── theme.py                  # BrandTheme: brand.yaml → color/font objects
│   ├── renderers/                # 12+ page type renderers
│   │   ├── __init__.py           # Renderer registry + fallback logic
│   │   ├── base.py               # BaseRenderer abstract class
│   │   ├── cover.py              # Full-bleed cover (image + overlay + title)
│   │   ├── section.py            # Chapter divider
│   │   ├── text_image.py         # Side-by-side text + image
│   │   ├── table.py              # Data table
│   │   ├── storyboard.py         # Storyboard table
│   │   ├── calendar.py           # Calendar / timeline
│   │   ├── grid.py               # Multi-image / card grid
│   │   ├── chart_placeholder.py  # Chart placeholder
│   │   ├── quote.py              # Pull quote / key message
│   │   ├── comparison.py         # Side-by-side comparison
│   │   ├── bullets.py            # Key points list (also fallback)
│   │   └── end_card.py           # Closing page
│   ├── utils/
│   │   ├── pptx_helpers.py       # Low-level python-pptx operations
│   │   └── file_reader.py        # Read .docx/.pdf/.txt/images → text
│   └── prompts/
│       └── system.py             # Dynamic system prompt (injects brand config)
│
├── brands/
│   ├── _template.yaml            # Blank brand template
│   └── therabody.yaml            # Example: Therabody brand config
│
├── examples/
│   ├── shooting-script/          # Storyboard example
│   ├── content-calendar/         # Content calendar example
│   ├── product-launch/           # Product launch example
│   └── social-plan/              # Social plan example
│
├── docs/
│   ├── getting-started.md
│   ├── use-cases.md              # Detailed scenarios + examples
│   ├── brand-config.md           # Brand configuration guide
│   ├── for-developers.md         # Contributing / extending
│   └── prompt-engineering.md     # System prompt design philosophy
│
└── tests/
    ├── test_ai.py                # AI backend tests (mocked API calls)
    ├── test_validator.py         # JSON validation + retry tests
    ├── test_builder.py           # End-to-end rendering tests
    ├── test_renderers/           # Per-renderer unit tests
    ├── test_file_reader.py       # Input format parsing tests
    ├── test_theme.py             # Brand config loading tests
    └── fixtures/                 # Sample brand.yaml, input files, expected JSON
```

---

## AI Layer Design

### Dual Backend Support

```python
# ai.py

class AIBackend:
    def generate(self, user_content: str, brand_config: dict) -> dict:
        """Call AI API, return structured JSON + design reasoning."""
        raise NotImplementedError

class ClaudeBackend(AIBackend):
    def generate(self, user_content, brand_config):
        # Uses anthropic SDK
        # System prompt from prompts/system.py
        # Returns: {"slides": [...], "reasoning": [...]}
        ...

class GeminiBackend(AIBackend):
    def generate(self, user_content, brand_config):
        # Uses google-genai SDK
        # Same system prompt, same output schema
        ...
```

Users choose in `brand.yaml`: `ai: claude` or `ai: gemini`, or via environment variable `BRANDDECK_AI=gemini`.

### Validation Layer

```python
# validator.py

class SlideValidator:
    def validate(self, ai_output: dict) -> dict:
        """
        Validates AI output against JSON Schema.
        On failure: retries AI call (max 2x) with error feedback.
        On unknown page type: maps to 'bullets' fallback.
        Returns validated, clean JSON ready for rendering.
        """
        ...
```

---

## Implementation Roadmap

### Phase 1: Core MVP — "It works, end to end"

| # | Task | Key Deliverable |
|---|---|---|
| 1 | Project scaffolding | `pyproject.toml`, project structure, dev tooling |
| 2 | `theme.py` | Load brand config from `brand.yaml` → `BrandTheme` object |
| 3 | `file_reader.py` | Read `.docx`, `.pdf`, `.txt` → normalized text |
| 4 | Extract from `gen_coaching_pptx.py` | → `utils/pptx_helpers.py` (reusable PPT primitives) |
| 5 | 6 core renderers | `cover`, `text_image`, `table`, `storyboard`, `bullets`, `end_card` |
| 6 | `builder.py` | Renderer registry + fallback logic + JSON → PPTX orchestration |
| 7 | `ai.py` + `prompts/system.py` | Claude backend + dynamic system prompt generation |
| 8 | `validator.py` | JSON Schema validation + auto-retry (max 2x) |
| 9 | `cli.py` | `brand-deck init` + `brand-deck make` + preview-confirm flow |
| 10 | Auto-open | Generated `.pptx` opens automatically after creation |
| 11 | Design reasoning | AI output includes per-page "why this layout" explanation |
| 12 | Therabody example | End-to-end validation with real brand config |

**Validation criteria:**
- `brand-deck make "Turn shooting script into PPT" --attach script.docx` → outputs `.pptx` comparable to manual creation
- Change colors in `brand.yaml` → re-run → confirm color changes apply
- Test 4 scenarios: script / calendar / product deck / competitive analysis → each produces reasonable page combinations

### Phase 2: Enrich Scenarios

| # | Task |
|---|---|
| 13 | Remaining renderers: `section`, `calendar`, `grid`, `quote`, `comparison`, `chart_placeholder` |
| 14 | Gemini backend |
| 15 | More examples: content-calendar, product-launch, social-plan |
| 16 | `--interactive` mode (full version with editing) |

### Phase 3: Open Source Release

| # | Task |
|---|---|
| 17 | README (bilingual EN/ZH) + `docs/` |
| 18 | PyPI publish (`pip install brand-deck`) |
| 19 | GitHub Actions CI (lint + test on PR) |
| 20 | Example screenshots + demo GIF |
| 21 | AOE Combo packaging (Floatboat integration) |

---

## Testing Strategy

```
NEW UX FLOWS:
  1. brand-deck init (interactive brand setup)
  2. brand-deck make (text input → PPTX)
  3. brand-deck make --attach (file input → PPTX)
  4. brand-deck make --interactive (preview → confirm → PPTX)

NEW DATA FLOWS:
  1. File → file_reader → normalized text
  2. Text + brand config → AI → structured JSON
  3. JSON → validator → validated JSON (or retry)
  4. Validated JSON → builder → renderer chain → .pptx

NEW ERROR PATHS:
  1. AI returns malformed JSON → validator catches → retry
  2. AI returns unknown page type → fallback renderer
  3. AI API timeout/rate-limit → retry with backoff
  4. File reader gets unsupported format → clear error
  5. Font not found → fallback to system font + warning
```

Every data flow is tested across 4 paths: **happy path**, **nil input**, **empty input**, **upstream error**.

---

## Performance Considerations

| Concern | Mitigation |
|---|---|
| AI latency (2-10s per call) | Show progress spinner. Preview mode avoids wasted renders. |
| Large input files | `file_reader.py` streams content, truncates at configurable max (default 50K chars) with warning. |
| Memory for large decks | Renderers process one slide at a time, not buffered in memory. |
| Token cost | System prompt is ~2K tokens. Typical 10-slide deck: ~5K input + ~3K output = ~$0.03 with Claude Haiku. |

---

## Deployment & Distribution

| Channel | Method |
|---|---|
| **PyPI** | `pip install brand-deck` — primary distribution |
| **GitHub** | Source code + issues + contributing guide |
| **AOE Combo** | Floatboat integration — use via natural language in chat |
| **Docker** (future) | `docker run brand-deck make "..."` for CI/CD pipelines |

---

## Long-Term Vision

```
  CURRENT STATE                    THIS PLAN (v1)                 12-MONTH IDEAL (v2+)
  ┌─────────────────┐    ┌──────────────────────────┐    ┌───────────────────────────┐
  │ Single-brand     │    │ Universal brand PPT       │    │ Marketing team AI         │
  │ hardcoded script │ →  │ generator CLI             │ →  │ content platform          │
  │ (gen_coaching_   │    │ 12+ page types            │    │ - Multi-brand management  │
  │  pptx.py)        │    │ Any marketing scenario    │    │ - Team sharing (brand.yaml│
  │ Only coaching    │    │ brand.yaml configuration  │    │   in shared repo)         │
  │ videos           │    │ Claude + Gemini support   │    │ - Web UI + REST API       │
  │ No AI layout     │    │ AI-powered layout         │    │ - Plugin marketplace      │
  │ decisions        │    │ decisions                 │    │   (custom renderers)      │
  │                  │    │                           │    │ - Learning from history   │
  └─────────────────┘    └──────────────────────────┘    │ - Multi-format output     │
                                                          │   (PDF, social cards,     │
                                                          │    email templates)        │
                                                          └───────────────────────────┘
```

---

## Reference Files

| File | Purpose |
|---|---|
| `~/Desktop/Therabody China Social/gen_coaching_pptx.py` | Source code for renderer & helper functions |
| `~/Desktop/Therabody China Social/Content/Therabody_Coaching_Video_Scripts_2026.pptx` | Visual output reference |
| `~/Downloads/Therabody-Presentation-Template_PowerPoint-Version_July-2024.pptx` | Brand template reference |

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
