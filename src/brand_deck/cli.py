# cli.py — 命令行入口
"""BrandDeck CLI: init brand config, generate PPT from content."""

from __future__ import annotations

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
    """BrandDeck — AI-Powered Marketing PPT Generator."""
    pass


@cli.command()
@click.option("--output", "-o", default="brand.yaml", help="Output path for brand config.")
def init(output: str):
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
    click.echo("\n🤖 AI Configuration")
    ai_backend = click.prompt("AI service", type=click.Choice(["claude", "gemini"]), default="claude")
    api_key = click.prompt("API Key", hide_input=True, default="")

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
    click.echo("⚠️  Remember to add brand.yaml to .gitignore (it contains your API key).")


@cli.command()
@click.argument("description")
@click.option("--attach", "-a", multiple=True, help="Attach file(s) or directory as input.")
@click.option("--output", "-o", default=None, help="Output .pptx path.")
@click.option("--config", "-c", default="brand.yaml", help="Brand config file.")
@click.option("--interactive", "-i", is_flag=True, help="Preview deck outline before generating.")
@click.option("--no-open", is_flag=True, help="Don't auto-open the generated file.")
def make(description: str, attach: tuple, output: str | None, config: str, interactive: bool, no_open: bool):
    """Generate a brand PPT from a description and optional attachments."""
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

    num_slides = len(slide_data.get("slides", []))
    click.echo(f"✅ AI generated {num_slides} slides")

    # Interactive preview
    if interactive:
        from brand_deck.builder import preview_deck
        preview = preview_deck(slide_data)
        click.echo(f"\n{preview}\n")

        if not click.confirm("Proceed with rendering?", default=True):
            click.echo("❌ Cancelled.")
            sys.exit(0)
    else:
        # Always show brief preview
        from brand_deck.builder import preview_deck
        preview = preview_deck(slide_data)
        click.echo(f"\n{preview}\n")

    # Render PPTX
    click.echo("🎨 Rendering PPTX...")
    from brand_deck.builder import build_deck

    if output is None:
        # Auto-generate filename from description
        safe_name = "".join(c if c.isalnum() or c in " -_" else "" for c in description[:40]).strip()
        safe_name = safe_name.replace(" ", "-") or "deck"
        output = f"{safe_name}.pptx"

    output_path = build_deck(slide_data, theme, output)
    click.echo(f"✅ Saved: {output_path}")

    # Show design reasoning
    summary = slide_data.get("summary", "")
    if summary:
        click.echo(f"\n💡 Design summary: {summary}")

    # Auto-open
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
