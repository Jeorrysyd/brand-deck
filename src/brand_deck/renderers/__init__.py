# renderers/__init__.py — 渲染器注册表 + 降级逻辑
"""Renderer registry. Maps page types to renderer functions."""

from __future__ import annotations

from typing import Callable

from brand_deck.theme import BrandTheme
from brand_deck.renderers.cover import render_cover
from brand_deck.renderers.text_image import render_text_image
from brand_deck.renderers.table import render_table
from brand_deck.renderers.storyboard import render_storyboard
from brand_deck.renderers.bullets import render_bullets
from brand_deck.renderers.end_card import render_end_card


# Registry: type name → renderer function
# Each renderer takes (slide_obj, slide_data: dict, theme: BrandTheme) -> None
RENDERER_REGISTRY: dict[str, Callable] = {
    "cover": render_cover,
    "text_image": render_text_image,
    "table": render_table,
    "storyboard": render_storyboard,
    "bullets": render_bullets,
    "end_card": render_end_card,
    # Phase 2 renderers (not yet implemented, fall back to bullets):
    # "section": render_section,
    # "calendar": render_calendar,
    # "grid": render_grid,
    # "quote": render_quote,
    # "comparison": render_comparison,
    # "chart_placeholder": render_chart_placeholder,
}

# Fallback renderer for unknown or unimplemented types
FALLBACK_TYPE = "bullets"


def get_renderer(page_type: str) -> Callable:
    """Get renderer function for a page type. Falls back to bullets if unknown."""
    renderer = RENDERER_REGISTRY.get(page_type)
    if renderer is None:
        return RENDERER_REGISTRY[FALLBACK_TYPE]
    return renderer
