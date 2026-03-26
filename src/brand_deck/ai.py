# ai.py — AI 后端：Claude / Gemini
"""AI backends for generating slide JSON from user content."""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod

from brand_deck.theme import BrandTheme
from brand_deck.prompts.system import generate_system_prompt


class AIBackend(ABC):
    """Abstract base class for AI backends."""

    @abstractmethod
    def generate(self, user_content: str, theme: BrandTheme) -> dict:
        """
        Call AI API with system prompt + user content.
        Returns parsed JSON dict with slide specifications.
        """
        raise NotImplementedError


class ClaudeBackend(AIBackend):
    """Anthropic Claude backend."""

    def generate(self, user_content: str, theme: BrandTheme) -> dict:
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "anthropic package is required for Claude backend.\n"
                "Install it: pip install anthropic"
            )

        if not theme.api_key:
            raise ValueError(
                "API key not configured.\n"
                "Set it in brand.yaml under ai.api_key, or set ANTHROPIC_API_KEY env var."
            )

        client = anthropic.Anthropic(api_key=theme.api_key)
        system_prompt = generate_system_prompt(theme)

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_content}
            ],
        )

        raw_text = message.content[0].text
        return _parse_json_response(raw_text)


class GeminiBackend(AIBackend):
    """Google Gemini backend."""

    def generate(self, user_content: str, theme: BrandTheme) -> dict:
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "google-genai package is required for Gemini backend.\n"
                "Install it: pip install google-genai"
            )

        api_key = theme.api_key
        if not api_key:
            import os
            api_key = os.environ.get("GOOGLE_API_KEY", "")

        if not api_key:
            raise ValueError(
                "API key not configured.\n"
                "Set it in brand.yaml under ai.api_key, or set GOOGLE_API_KEY env var."
            )

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-pro")
        system_prompt = generate_system_prompt(theme)

        response = model.generate_content(
            f"{system_prompt}\n\n---\n\nUser content:\n\n{user_content}"
        )

        raw_text = response.text
        return _parse_json_response(raw_text)


def get_backend(theme: BrandTheme) -> AIBackend:
    """Get the appropriate AI backend based on theme config."""
    backend_name = theme.ai_backend.lower()

    if backend_name == "claude":
        return ClaudeBackend()
    elif backend_name == "gemini":
        return GeminiBackend()
    else:
        raise ValueError(
            f"Unknown AI backend: {backend_name}\n"
            f"Supported backends: claude, gemini"
        )


def _parse_json_response(raw_text: str) -> dict:
    """
    Parse JSON from AI response.
    Handles common issues: markdown code fences, trailing text, etc.
    """
    text = raw_text.strip()

    # Remove markdown code fences if present
    if text.startswith("```"):
        # Remove opening fence (with optional language tag)
        text = re.sub(r"^```\w*\n?", "", text)
        # Remove closing fence
        text = re.sub(r"\n?```\s*$", "", text)
        text = text.strip()

    # Try to find JSON object in the text
    # Look for the first { and last }
    first_brace = text.find("{")
    last_brace = text.rfind("}")

    if first_brace == -1 or last_brace == -1:
        raise ValueError(f"No JSON object found in AI response:\n{raw_text[:500]}")

    json_str = text[first_brace : last_brace + 1]

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse JSON from AI response: {e}\n"
            f"Raw text (first 500 chars):\n{raw_text[:500]}"
        )
