# builder.py — 渲染编排引擎
"""Orchestrate slide rendering: JSON → PPTX using renderer registry."""

from __future__ import annotations

import json
from pathlib import Path

from pptx import Presentation

from brand_deck.theme import BrandTheme
from brand_deck.renderers import get_renderer
from brand_deck.utils.pptx_helpers import create_presentation


def build_deck(slide_data: dict, theme: BrandTheme, output_path: str | Path) -> Path:
    """
    Build a PPTX presentation from validated slide JSON.

    Args:
        slide_data: Validated JSON dict with "slides" array.
        theme: BrandTheme for styling.
        output_path: Where to save the .pptx file.

    Returns:
        Path to the saved .pptx file.
    """
    output_path = Path(output_path)
    prs = create_presentation(theme)

    slides = slide_data.get("slides", [])

    for i, slide_spec in enumerate(slides):
        page_type = slide_spec.get("type", "bullets")
        renderer = get_renderer(page_type)

        try:
            renderer(prs, slide_spec, theme)
        except Exception as e:
            # If a renderer crashes, fall back to bullets
            from brand_deck.renderers.bullets import render_bullets
            fallback_data = {
                "title": slide_spec.get("title", f"Slide {i + 1}"),
                "points": [
                    f"[Rendering error for type '{page_type}': {e}]",
                    "Content has been preserved as text below:",
                    json.dumps(slide_spec, ensure_ascii=False, indent=2)[:300],
                ],
            }
            render_bullets(prs, fallback_data, theme)

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(output_path))

    return output_path


def preview_deck(slide_data: dict) -> str:
    """
    Generate a text preview of the deck structure for user confirmation.

    Returns a formatted string showing slide outline.
    """
    slides = slide_data.get("slides", [])
    lines = [f"📊 Deck Preview — {len(slides)} slides\n"]

    for i, slide_spec in enumerate(slides, 1):
        page_type = slide_spec.get("type", "unknown")
        title = slide_spec.get("title", slide_spec.get("quote", ""))
        reasoning = slide_spec.get("reasoning", "")

        # Type emoji mapping
        emoji = {
            "cover": "🎬",
            "section": "📑",
            "text_image": "🖼️",
            "table": "📊",
            "storyboard": "🎥",
            "calendar": "📅",
            "grid": "📐",
            "quote": "💬",
            "comparison": "⚖️",
            "bullets": "📝",
            "end_card": "🎯",
        }.get(page_type, "📄")

        line = f"  {i}. {emoji} [{page_type}] {title}"
        if reasoning:
            line += f"\n     └─ {reasoning}"
        lines.append(line)

    summary = slide_data.get("summary", "")
    if summary:
        lines.append(f"\n💡 Design summary: {summary}")

    return "\n".join(lines)
