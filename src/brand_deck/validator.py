# validator.py — JSON Schema 校验 + 自动重试
"""Validate AI-generated slide JSON against schema. Auto-retry on failure."""

from __future__ import annotations

import json
from typing import Any

import jsonschema

from brand_deck.theme import BrandTheme


# Valid page types
VALID_PAGE_TYPES = {
    "cover", "section", "text_image", "table", "storyboard",
    "calendar", "grid", "quote", "comparison", "bullets", "end_card",
}

# JSON Schema for the slides output
SLIDE_SCHEMA = {
    "type": "object",
    "required": ["slides"],
    "properties": {
        "slides": {
            "type": "array",
            "minItems": 2,
            "items": {
                "type": "object",
                "required": ["type"],
                "properties": {
                    "type": {"type": "string"},
                    "reasoning": {"type": "string"},
                },
            },
        },
        "summary": {"type": "string"},
    },
}


class ValidationError(Exception):
    """Raised when AI output fails validation."""
    pass


def validate_slides(data: dict) -> dict:
    """
    Validate slide JSON against schema.
    - Checks JSON structure
    - Normalizes unknown page types to 'bullets' (fallback)
    - Ensures first slide is cover and last is end_card
    Returns cleaned, validated data.
    """
    # Step 1: Schema validation
    try:
        jsonschema.validate(instance=data, schema=SLIDE_SCHEMA)
    except jsonschema.ValidationError as e:
        raise ValidationError(f"JSON Schema validation failed: {e.message}")

    slides = data["slides"]

    # Step 2: Normalize unknown page types → bullets fallback
    for slide in slides:
        page_type = slide.get("type", "").lower().strip()
        if page_type not in VALID_PAGE_TYPES:
            original = slide.get("type", "unknown")
            slide["type"] = "bullets"
            slide.setdefault("reasoning", "")
            slide["reasoning"] += f" [Fallback: original type '{original}' not recognized]"

    # Step 3: Ensure cover + end_card
    if slides[0]["type"] != "cover":
        # Prepend a default cover
        slides.insert(0, {
            "type": "cover",
            "title": data.get("title", "Presentation"),
            "reasoning": "Auto-added: first slide must be a cover.",
        })

    if slides[-1]["type"] != "end_card":
        slides.append({
            "type": "end_card",
            "title": "Thank You",
            "reasoning": "Auto-added: last slide must be an end card.",
        })

    data["slides"] = slides
    return data


def validate_with_retry(
    generate_fn,
    user_content: str,
    theme: BrandTheme,
    max_retries: int = 2,
) -> dict:
    """
    Call AI generate function and validate output.
    On validation failure, retry with error feedback (up to max_retries).
    """
    last_error = None

    for attempt in range(1 + max_retries):
        try:
            # Generate
            if attempt == 0:
                content = user_content
            else:
                # Add error feedback to help AI self-correct
                content = (
                    f"{user_content}\n\n"
                    f"---\n"
                    f"IMPORTANT: Your previous response had an error:\n"
                    f"{last_error}\n\n"
                    f"Please fix the error and output valid JSON only."
                )

            raw_data = generate_fn(content, theme)

            # Validate
            validated = validate_slides(raw_data)
            return validated

        except (ValidationError, ValueError, KeyError) as e:
            last_error = str(e)
            if attempt < max_retries:
                continue
            else:
                raise ValidationError(
                    f"AI output failed validation after {max_retries + 1} attempts.\n"
                    f"Last error: {last_error}"
                )
