"""Parsing helpers for conversational intake answers."""

import re


def parse_duration(raw: str) -> float:
    value = raw.strip().lower()
    if value == "half a day":
        return 4.0

    match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(days?|d)", value)
    if match:
        return float(match.group(1)) * 8

    match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(hours?|hrs?|h)", value)
    if match:
        return float(match.group(1))

    match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(minutes?|mins?|m)", value)
    if match:
        return float(match.group(1)) / 60

    if re.fullmatch(r"\d+(?:\.\d+)?", value):
        return float(value)

    raise ValueError("Enter a duration such as '2 hours', '90 minutes', or 'half a day'.")


def parse_level(raw: str) -> int:
    return _parse_choice(raw, "level")


def parse_tier(raw: str) -> int:
    return _parse_choice(raw, "tier")


def parse_outline_path(raw: str) -> str:
    return _parse_mapped_choice(
        raw,
        {"1": "trainer_supplied", "2": "research_assisted"},
        "outline path must be 1 or 2.",
    )


def parse_output_language(raw: str) -> str:
    return _parse_mapped_choice(
        raw,
        {"1": "en", "2": "nl", "3": "bilingual"},
        "output language must be 1, 2, or 3.",
    )


def _parse_choice(raw: str, field: str) -> int:
    try:
        value = int(raw.strip())
    except (AttributeError, ValueError) as exc:
        raise ValueError(f"{field} must be 1, 2, or 3.") from exc
    if value not in (1, 2, 3):
        raise ValueError(f"{field} must be 1, 2, or 3.")
    return value


def _parse_mapped_choice(raw: str, choices: dict[str, str], error: str) -> str:
    try:
        return choices[raw.strip()]
    except (AttributeError, KeyError) as exc:
        raise ValueError(error) from exc


def coerce_knowledge_level(raw: str) -> str:
    value = raw.strip().lower()
    if value not in ("beginner", "intermediate", "advanced"):
        raise ValueError("Knowledge level must be beginner, intermediate, or advanced.")
    return value


def derive_slide_target(duration_hours: float, tier: int) -> int:
    base = int(duration_hours * 12)
    if tier == 1:
        return max(30, min(base, 50))
    if tier == 2:
        return max(30, min(base, 50))
    if tier == 3:
        return max(30, min(base, 80))
    raise ValueError("tier must be 1, 2, or 3")
