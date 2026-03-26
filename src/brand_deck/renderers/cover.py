# renderers/cover.py — 封面页渲染器
"""Render a full-bleed cover slide with title and optional subtitle."""

from __future__ import annotations

from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

from brand_deck.theme import BrandTheme
from brand_deck.utils.pptx_helpers import (
    add_blank_slide, add_shape, add_textbox, set_slide_bg,
    add_image_safe, SLIDE_WIDTH, SLIDE_HEIGHT,
)


def render_cover(prs, slide_data: dict, theme: BrandTheme) -> None:
    """Render a cover slide."""
    slide = add_blank_slide(prs)

    # Dark background
    set_slide_bg(slide, theme.primary_rgb)

    # Accent strip at bottom
    add_shape(
        slide,
        left=0,
        top=SLIDE_HEIGHT - Inches(0.15),
        width=SLIDE_WIDTH,
        height=Inches(0.15),
        fill_color=theme.accent_rgb,
    )

    # Title
    title = slide_data.get("title", "Presentation")
    add_textbox(
        slide,
        left=Inches(1.2),
        top=Inches(2.2),
        width=Inches(10.9),
        height=Inches(2.0),
        text=title,
        font_name=theme.heading_font,
        font_size=48,
        font_color=theme.text_light_rgb,
        bold=True,
        alignment=PP_ALIGN.LEFT,
    )

    # Subtitle
    subtitle = slide_data.get("subtitle", "")
    if subtitle:
        add_textbox(
            slide,
            left=Inches(1.2),
            top=Inches(4.4),
            width=Inches(10.9),
            height=Inches(1.0),
            text=subtitle,
            font_name=theme.body_font,
            font_size=22,
            font_color=theme.accent_rgb,
            bold=False,
            alignment=PP_ALIGN.LEFT,
        )

    # Logo (if available)
    if theme.logo_path:
        add_image_safe(
            slide,
            theme.logo_path,
            left=Inches(1.2),
            top=Inches(6.0),
            height=Inches(0.8),
        )
