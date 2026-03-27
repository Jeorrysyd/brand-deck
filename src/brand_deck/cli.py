# cli.py — 命令行入口
"""BrandDeck CLI: init brand config, generate PPT from content."""

from __future__ import annotations

import json
import os
import sys
import platform
import subprocess
from pathlib import Path

import click

from brand_deck.theme import BrandTheme


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """BrandDeck — AI-Powered Marketing PPT Generator.

    \b
    Two usage modes:
      1. Standalone: brand-deck make "..." --attach file.pdf
         (uses Claude/Gemini API key in brand.yaml)

      2. Agent mode: brand-deck render slides.json
         (Agent generates JSON, brand-deck just renders — no API key needed)
    """
    pass


@cli.command()
@click.option("--output", "-o", default="brand.yaml", help="Output path for brand config.")
@click.option("--agent", is_flag=True, help="Agent mode: skip API key setup.")
def init(output: str, agent: bool):
    """Initialize brand configuration interactively."""
    click.echo("🎨 BrandDeck Brand Setup\n")

    name = click.prompt("Brand name", default="MyBrand")
    primary = click.prompt("Primary color (hex)", default="#000000")
    accent = click.prompt("Accent color (hex)", default="#FF6600")
    background = click.prompt("Background color (hex)", default="#FFFFFF")
    heading_font = click.prompt("Heading font", default="Arial")
    body_font = click.prompt("Body font", default="Arial")
    tone = click.prompt("Brand tone (e.g., professional, bold, warm)", default="professional")
    logo = click.prompt("Logo file path (optional, press Enter to skip)", default="", show_default=False)
    template = click.prompt("Brand PPTX template (optional, press Enter to skip)", default="", show_default=False)

    # AI config
    if agent:
        click.echo("\n🤖 Agent mode — AI is handled by your agent (Claude/Floatboat).")
        click.echo("   Skipping API key setup. Use 'brand-deck render' to generate PPT from JSON.\n")
        ai_backend = "claude"
        api_key = ""
    else:
        click.echo("\n🤖 AI Configuration")
        click.echo("   (Skip if you'll use Agent mode — Claude Code / Floatboat / Cursor)")
        ai_backend = click.prompt(
            "AI service",
            type=click.Choice(["claude", "gemini"]),
            default="claude",
        )
        api_key = click.prompt(
            "API Key (press Enter to skip — use env var or Agent mode later)",
            hide_input=True,
            default="",
            show_default=False,
        )

    theme = BrandTheme(
        name=name,
        primary=primary,
        accent=accent,
        background=background,
        heading_font=heading_font,
        body_font=body_font,
        tone=tone,
        logo_path=logo or None,
        template_path=template or None,
        ai_backend=ai_backend,
        api_key=api_key,
    )

    theme.to_yaml(output)
    click.echo(f"\n✅ Brand config saved: {output}")

    if api_key:
        click.echo("⚠️  brand.yaml contains your API key — ensure it's in .gitignore.")
    else:
        click.echo("ℹ️  No API key stored. Use Agent mode (brand-deck render) or set ANTHROPIC_API_KEY env var.")


@cli.command()
@click.argument("description")
@click.option("--attach", "-a", multiple=True, help="Attach file(s) or directory as input.")
@click.option("--output", "-o", default=None, help="Output .pptx path.")
@click.option("--config", "-c", default="brand.yaml", help="Brand config file.")
@click.option("--interactive", "-i", is_flag=True, help="Preview deck outline before generating.")
@click.option("--no-open", is_flag=True, help="Don't auto-open the generated file.")
def make(description: str, attach: tuple, output: str | None, config: str, interactive: bool, no_open: bool):
    """Generate a brand PPT from a description and optional attachments.

    Calls Claude/Gemini directly — requires API key in brand.yaml or env var.
    For Agent mode (no API key), use: brand-deck render <json_file>
    """
    # Load brand config
    config_path = Path(config)
    if not config_path.exists():
        click.echo(f"❌ Brand config not found: {config}")
        click.echo("Run 'brand-deck init' first to create your brand configuration.")
        sys.exit(1)

    click.echo("🔧 Loading brand config...")
    theme = BrandTheme.from_yaml(config_path)

    # Build user content from description + attachments
    content_parts = [description]

    if attach:
        click.echo(f"📎 Reading {len(attach)} attachment(s)...")
        from brand_deck.utils.file_reader import read_multiple
        attached_text = read_multiple(attach)
        content_parts.append(attached_text)

    user_content = "\n\n".join(content_parts)

    # Truncate if too long (safety valve)
    max_chars = 50000
    if len(user_content) > max_chars:
        click.echo(f"⚠️  Input truncated to {max_chars} characters (was {len(user_content)})")
        user_content = user_content[:max_chars]

    # Call AI
    click.echo(f"🤖 Generating slide structure via {theme.ai_backend}...")
    from brand_deck.ai import get_backend
    from brand_deck.validator import validate_with_retry

    backend = get_backend(theme)

    try:
        slide_data = validate_with_retry(
            backend.generate,
            user_content,
            theme,
            max_retries=2,
        )
    except Exception as e:
        click.echo(f"❌ AI generation failed: {e}")
        sys.exit(1)

    _render_and_save(slide_data, theme, description, output, interactive, no_open)


@cli.command()
@click.argument("json_source", required=False)
@click.option("--output", "-o", default=None, help="Output .pptx path.")
@click.option("--config", "-c", default="brand.yaml", help="Brand config file.")
@click.option("--no-open", is_flag=True, help="Don't auto-open the generated file.")
def render(json_source: str | None, output: str | None, config: str, no_open: bool):
    """Render a PPTX from pre-generated slide JSON — no API key needed.

    \b
    Agent mode usage:
      brand-deck render slides.json
      brand-deck render '{"slides": [...]}'
      cat slides.json | brand-deck render

    \b
    The JSON must follow the BrandDeck slide schema:
      {
        "slides": [
          {"type": "cover", "title": "...", "subtitle": "..."},
          {"type": "bullets", "title": "...", "points": ["...", "..."]},
          ...
        ],
        "summary": "optional design summary"
      }

    Use 'brand-deck schema' to see full schema.
    """
    # Load brand config (only needs brand info, not AI key)
    config_path = Path(config)
    if not config_path.exists():
        click.echo(f"❌ Brand config not found: {config}")
        click.echo("Run 'brand-deck init' first to set up your brand colors and fonts.")
        sys.exit(1)

    click.echo("🔧 Loading brand config...")
    theme = BrandTheme.from_yaml(config_path)

    # Read JSON — from argument (file path or inline JSON string), or stdin
    raw_json = None

    if json_source:
        src_path = Path(json_source)
        if src_path.exists():
            # It's a file path
            click.echo(f"📂 Reading JSON from file: {json_source}")
            raw_json = src_path.read_text(encoding="utf-8")
        else:
            # Treat as inline JSON string
            click.echo("📋 Reading inline JSON...")
            raw_json = json_source
    elif not sys.stdin.isatty():
        # Read from stdin (pipe)
        click.echo("📥 Reading JSON from stdin...")
        raw_json = sys.stdin.read()
    else:
        click.echo("❌ No JSON provided.")
        click.echo("Usage:")
        click.echo("  brand-deck render slides.json")
        click.echo("  brand-deck render '{\"slides\": [...]}'")
        click.echo("  cat slides.json | brand-deck render")
        sys.exit(1)

    # Parse and validate JSON
    try:
        slide_data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        click.echo(f"❌ Invalid JSON: {e}")
        sys.exit(1)

    if "slides" not in slide_data or not isinstance(slide_data["slides"], list):
        click.echo("❌ JSON must contain a 'slides' array.")
        click.echo("   Expected: {\"slides\": [{\"type\": \"cover\", ...}, ...]}")
        sys.exit(1)

    num_slides = len(slide_data["slides"])
    click.echo(f"✅ Loaded {num_slides} slides from JSON")

    # Show preview
    from brand_deck.builder import preview_deck
    preview = preview_deck(slide_data)
    click.echo(f"\n{preview}\n")

    # Determine output filename
    if output is None:
        title = slide_data["slides"][0].get("title", "deck") if slide_data["slides"] else "deck"
        safe_name = "".join(c if c.isalnum() or c in " -_" else "" for c in str(title)[:40]).strip()
        safe_name = safe_name.replace(" ", "-") or "deck"
        output = f"{safe_name}.pptx"

    # Render
    click.echo("🎨 Rendering PPTX...")
    from brand_deck.builder import build_deck
    output_path = build_deck(slide_data, theme, output)
    click.echo(f"✅ Saved: {output_path}")

    summary = slide_data.get("summary", "")
    if summary:
        click.echo(f"\n💡 Design summary: {summary}")

    if not no_open:
        _open_file(str(output_path))


@cli.command()
def schema():
    """Print the BrandDeck slide JSON schema for Agent mode."""
    schema_example = {
        "slides": [
            {
                "type": "cover",
                "title": "Slide title",
                "subtitle": "Optional subtitle",
                "image": "optional/path/to/image.jpg",
                "reasoning": "Why this layout was chosen (optional)"
            },
            {
                "type": "bullets",
                "title": "Section title",
                "points": ["Point 1", "Point 2", "Point 3"]
            },
            {
                "type": "text_image",
                "title": "Section title",
                "body": "Body text content",
                "image": "optional/image.jpg",
                "layout": "left"
            },
            {
                "type": "table",
                "title": "Table title",
                "headers": ["Column 1", "Column 2", "Column 3"],
                "rows": [["Row1Col1", "Row1Col2", "Row1Col3"]]
            },
            {
                "type": "end_card",
                "title": "Thank You",
                "subtitle": "contact@brand.com"
            }
        ],
        "summary": "Optional: overall design rationale"
    }

    click.echo("BrandDeck Slide JSON Schema\n")
    click.echo("Available page types: cover, section, text_image, table, storyboard,")
    click.echo("  calendar, grid, chart_placeholder, quote, comparison, bullets, end_card\n")
    click.echo("Example structure:")
    click.echo(json.dumps(schema_example, indent=2, ensure_ascii=False))


def _render_and_save(
    slide_data: dict,
    theme: BrandTheme,
    description: str,
    output: str | None,
    interactive: bool,
    no_open: bool,
) -> None:
    """Shared render + save logic for `make` and `render` commands."""
    num_slides = len(slide_data.get("slides", []))
    click.echo(f"✅ AI generated {num_slides} slides")

    from brand_deck.builder import preview_deck, build_deck

    # Interactive preview
    preview = preview_deck(slide_data)
    click.echo(f"\n{preview}\n")

    if interactive:
        if not click.confirm("Proceed with rendering?", default=True):
            click.echo("❌ Cancelled.")
            sys.exit(0)

    # Render PPTX
    click.echo("🎨 Rendering PPTX...")

    if output is None:
        safe_name = "".join(c if c.isalnum() or c in " -_" else "" for c in description[:40]).strip()
        safe_name = safe_name.replace(" ", "-") or "deck"
        output = f"{safe_name}.pptx"

    output_path = build_deck(slide_data, theme, output)
    click.echo(f"✅ Saved: {output_path}")

    summary = slide_data.get("summary", "")
    if summary:
        click.echo(f"\n💡 Design summary: {summary}")

    if not no_open:
        _open_file(str(output_path))


def _open_file(path: str) -> None:
    """Open a file with the system's default application."""
    try:
        system = platform.system()
        if system == "Darwin":  # macOS
            subprocess.Popen(["open", path])
        elif system == "Windows":
            os.startfile(path)
        elif system == "Linux":
            subprocess.Popen(["xdg-open", path])
    except Exception:
        pass  # Silently fail — not critical


if __name__ == "__main__":
    cli()
