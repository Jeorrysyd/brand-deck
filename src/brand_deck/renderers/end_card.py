# renderers/end_card.py — 尾页渲染器
"""Render a closing/end card slide with CTA."""

from __future__ import annotations

from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

from brand_deck.theme import BrandTheme
from brand_deck.utils.pptx_helpers import (
    add_blank_slide, add_textbox, add_shape, add_image_safe,
    set_slide_bg, SLIDE_WIDTH, SLIDE_HEIGHT,
)


def render_end_card(prs, slide_data: dict, theme: BrandTheme) -> None:
    """Render an end card / closing slide."""
    slide = add_blank_slide(prs)

    # Dark background (same as cover for symmetry)
    set_slide_bg(slide, theme.primary_rgb)

    # Accent strip at top
    add_shape(
        slide,
        left=0,
        top=0,
        width=SLIDE_WIDTH,
        height=Inches(0.15),
        fill_color=theme.accent_rgb,
    )

    # Title (e.g., "Thank You")
    title = slide_data.get("title", "Thank You")
    add_textbox(
        slide,
        left=Inches(1.2),
        top=Inches(2.5),
        width=Inches(10.9),
        height=Inches(1.5),
        text=title,
        font_name=theme.heading_font,
        font_size=44,
        font_color=theme.text_light_rgb,
        bold=True,
        alignment=PP_ALIGN.CENTER,
    )

    # Subtitle / CTA
    subtitle = slide_data.get("subtitle", "")
    cta = slide_data.get("cta", "")
    sub_text = subtitle or cta

    if sub_text:
        add_textbox(
            slide,
            left=Inches(1.2),
            top=Inches(4.2),
            width=Inches(10.9),
            height=Inches(1.0),
            text=sub_text,
            font_name=theme.body_font,
            font_size=20,
            font_color=theme.accent_rgb,
            bold=False,
            alignment=PP_ALIGN.CENTER,
        )

    # Logo
    if theme.logo_path:
        add_image_safe(
            slide,
            theme.logo_path,
            left=Inches(5.7),
            top=Inches(5.8),
            height=Inches(0.8),
        )
