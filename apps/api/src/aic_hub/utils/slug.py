"""Slug generation utilities."""

import re
from unidecode import unidecode


def slugify(text: str, max_length: int = 50) -> str:
    """Convert text to URL-safe slug.

    Args:
        text: Text to convert to slug
        max_length: Maximum length of slug

    Returns:
        URL-safe slug string
    """
    # Convert to ASCII
    text = unidecode(text)
    # Lowercase and replace non-alphanumeric chars with hyphens
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[-\s]+', '-', text)
    # Truncate to max length
    return text[:max_length].rstrip('-')