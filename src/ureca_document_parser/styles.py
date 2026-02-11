"""Shared heading-style utilities for HWP and HWPX parsers.

Maps style names (Korean / English) to heading levels.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Heading style patterns
# ---------------------------------------------------------------------------
# Keys are lowercased for case-insensitive matching.
HEADING_STYLE_PATTERNS: dict[str, int] = {
    "outline1": 1,
    "outline2": 2,
    "outline3": 3,
    "outline4": 4,
    "outline5": 5,
    "outline6": 6,
    "개요 1": 1,
    "개요 2": 2,
    "개요 3": 3,
    "개요 4": 4,
    "개요 5": 5,
    "개요 6": 6,
    "제목": 1,
    "부제목": 2,
    "title": 1,
    "subtitle": 2,
}


def heading_level_from_style(style_name: str) -> int:
    """Return heading level (1-6) for *style_name*, or 0 for normal text."""
    lower = style_name.lower()
    for pattern, level in HEADING_STYLE_PATTERNS.items():
        if pattern in lower:
            return level
    return 0
