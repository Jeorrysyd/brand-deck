# theme.py — 品牌主题管理
"""Load brand configuration from brand.yaml and provide BrandTheme objects."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from pptx.util import Pt
from pptx.dml.color import RGBColor


def hex_to_rgb(hex_color: str) -> RGBColor:
    """Convert hex color string to python-pptx RGBColor."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return RGBColor(r, g, b)


@dataclass
class BrandTheme:
    """Brand theme configuration loaded from brand.yaml."""

    name: str = "Brand"
    primary: str = "#000000"
    accent: str = "#FF6600"
    background: str = "#FFFFFF"
    text_light: str = "#FFFFFF"
    text_dark: str = "#333333"
    heading_font: str = "Arial"
    body_font: str = "Arial"
    tone: str = "professional"
    logo_path: str | None = None
    template_path: str | None = None

    # AI config
    ai_backend: str = "claude"
    api_key: str = ""
    api_base_url: str | None = None

    @property
    def primary_rgb(self) -> RGBColor:
        return hex_to_rgb(self.primary)

    @property
    def accent_rgb(self) -> RGBColor:
        return hex_to_rgb(self.accent)

    @property
    def bg_rgb(self) -> RGBColor:
        return hex_to_rgb(self.background)

    @property
    def text_light_rgb(self) -> RGBColor:
        return hex_to_rgb(self.text_light)

    @property
    def text_dark_rgb(self) -> RGBColor:
        return hex_to_rgb(self.text_dark)

    @classmethod
    def from_yaml(cls, path: str | Path) -> "BrandTheme":
        """Load a BrandTheme from a YAML file."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Brand config not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        colors = data.get("colors", {})
        fonts = data.get("fonts", {})
        ai = data.get("ai", {})

        return cls(
            name=data.get("name", "Brand"),
            primary=colors.get("primary", "#000000"),
            accent=colors.get("accent", "#FF6600"),
            background=colors.get("background", "#FFFFFF"),
            text_light=colors.get("text_light", "#FFFFFF"),
            text_dark=colors.get("text_dark", "#333333"),
            heading_font=fonts.get("heading", "Arial"),
            body_font=fonts.get("body", "Arial"),
            tone=data.get("tone", "professional"),
            logo_path=data.get("logo"),
            template_path=data.get("template"),
            ai_backend=ai.get("backend", os.environ.get("BRANDDECK_AI", "claude")),
            api_key=ai.get("api_key", os.environ.get("ANTHROPIC_API_KEY", "")),
            api_base_url=ai.get("base_url"),
        )

    def to_yaml(self, path: str | Path) -> None:
        """Save this BrandTheme to a YAML file."""
        data = {
            "name": self.name,
            "colors": {
                "primary": self.primary,
                "accent": self.accent,
                "background": self.background,
                "text_light": self.text_light,
                "text_dark": self.text_dark,
            },
            "fonts": {
                "heading": self.heading_font,
                "body": self.body_font,
            },
            "tone": self.tone,
            "logo": self.logo_path,
            "template": self.template_path,
            "ai": {
                "backend": self.ai_backend,
                "api_key": self.api_key,
            },
        }
        if self.api_base_url:
            data["ai"]["base_url"] = self.api_base_url

        path = Path(path)
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def to_prompt_context(self) -> str:
        """Generate brand context string for injection into AI system prompt."""
        return (
            f"Brand: {self.name}\n"
            f"Primary color: {self.primary}\n"
            f"Accent color: {self.accent}\n"
            f"Background color: {self.background}\n"
            f"Heading font: {self.heading_font}\n"
            f"Body font: {self.body_font}\n"
            f"Brand tone: {self.tone}"
        )
