# renderers/text_image.py — 图文并排页渲染器
"""Render a side-by-side text + image slide."""

from __future__ import annotations

from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

from brand_deck.theme import BrandTheme
from brand_deck.utils.pptx_helpers import (
    add_blank_slide, add_title, add_textbox, add_image_safe, add_shape, set_slide_bg,
    SLIDE_WIDTH, SLIDE_HEIGHT,
)


def render_text_image(prs, slide_data: dict, theme: BrandTheme) -> None:
    """Render a text + image slide. Image on left or right."""
    slide = add_blank_slide(prs)
    set_slide_bg(slide, theme.bg_rgb)

    title = slide_data.get("title", "")
    body = slide_data.get("body", "")
    image_pos = slide_data.get("image_position", "right")
    image_url = slide_data.get("image_url")

    # Title across top
    if title:
        add_title(slide, title, theme, top=Inches(0.6))

    # Layout: text on one side, image placeholder on the other
    if image_pos == "left":
        text_left = Inches(7.0)
        img_left = Inches(0.8)
    else:
        text_left = Inches(0.8)
        img_left = Inches(7.0)

    text_width = Inches(5.5)
    img_width = Inches(5.5)
    content_top = Inches(2.0)
    content_height = Inches(4.8)

    # Body text
    if body:
        add_textbox(
            slide,
            left=text_left,
            top=content_top,
            width=text_width,
            height=content_height,
            text=body,
            font_name=theme.body_font,
            font_size=16,
            font_color=theme.text_dark_rgb,
            alignment=PP_ALIGN.LEFT,
        )

    # Image or placeholder
    if image_url:
        add_image_safe(
            slide, image_url,
            left=img_left, top=content_top,
            width=img_width, height=content_height,
        )
    else:
        # Image placeholder box
        add_shape(
            slide,
            left=img_left, top=content_top,
            width=img_width, height=content_height,
            fill_color=theme.accent_rgb,
        )
        add_textbox(
            slide,
            left=img_left + Inches(1.0),
            top=content_top + Inches(2.0),
            width=Inches(3.5),
            height=Inches(0.8),
            text="[ Image ]",
            font_name=theme.body_font,
            font_size=18,
            font_color=theme.text_light_rgb,
            alignment=PP_ALIGN.CENTER,
        )
