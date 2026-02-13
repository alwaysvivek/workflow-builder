"""
Input sanitization utilities for zero-trust rendering.

All user-supplied text is sanitized at the Pydantic schema layer
before it reaches the database or LLM. This ensures defense-in-depth:
even if the frontend escaping is bypassed, the backend will never
store raw HTML/script content.
"""

import re
from html import escape as html_escape


def strip_html_tags(text: str) -> str:
    """Remove all HTML tags from input text."""
    return re.sub(r'<[^>]+>', '', text)


def sanitize_text(text: str, max_length: int = 10000) -> str:
    """
    Full sanitization pipeline for user-supplied text:
    1. Strip leading/trailing whitespace
    2. Remove HTML tags (defense-in-depth against XSS)
    3. Escape remaining HTML entities
    4. Enforce maximum length
    """
    text = text.strip()
    text = strip_html_tags(text)
    text = html_escape(text)
    if len(text) > max_length:
        text = text[:max_length]
    return text


def sanitize_name(text: str, max_length: int = 200) -> str:
    """Sanitize short-form fields like workflow names."""
    text = text.strip()
    text = strip_html_tags(text)
    text = html_escape(text)
    if len(text) > max_length:
        text = text[:max_length]
    return text
