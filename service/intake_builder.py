"""Build a complete, valid Person A intake from the frontend's friendly answers.

The web client only collects a handful of free-text answers (topic, audience,
knowledge level, duration, objective) plus a tier. This module fills in the rest
of the strict intake contract: it coerces the loose fields, derives slide_target,
defaults the optional choices, and injects the required Maverx constants.
"""

from typing import Any

from intake.parser import derive_slide_target, parse_duration
from intake.validator import DIDACTIC_BLOCKS, SPEAKER_NOTES_FIELDS

KNOWLEDGE_LEVELS = ("beginner", "intermediate", "advanced")


def coerce_knowledge_level(raw: Any) -> str:
    """Map loose free text ("Beginners", "advanced learners") to the enum."""
    text = str(raw or "").strip().lower()
    if "begin" in text or "novice" in text or "new" in text:
        return "beginner"
    if "inter" in text or "some" in text:
        return "intermediate"
    if "adv" in text or "expert" in text or "senior" in text:
        return "advanced"
    if text in KNOWLEDGE_LEVELS:
        return text
    return "beginner"


def coerce_duration_hours(raw: Any) -> float:
    """Accept a number or natural-language duration; default to 2 hours."""
    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        return float(raw)
    try:
        return parse_duration(str(raw))
    except (ValueError, TypeError):
        return 2.0


def build_intake(answers: dict) -> dict:
    """Assemble a full intake dict from the client's answers.

    `answers` may include: tier, topic, audience, knowledge_level, duration,
    primary_objective, outline_path (optional), output_language (optional).
    Validation/scoring is performed by the caller via `validate_intake`.
    """
    tier = answers.get("tier", 1)
    if tier not in (1, 2, 3):
        tier = 1

    duration_hours = coerce_duration_hours(answers.get("duration"))

    return {
        "tier": tier,
        # The web flow builds one module at a time, so level is always 1
        # (Essentials). Tier alone decides how many dependent decks are produced.
        "level": 1,
        "topic": str(answers.get("topic", "")).strip(),
        "audience": str(answers.get("audience", "")).strip(),
        "knowledge_level": coerce_knowledge_level(answers.get("knowledge_level")),
        "duration_hours": duration_hours,
        "primary_objective": str(answers.get("primary_objective", "")).strip(),
        "outline_path": answers.get("outline_path", "research_assisted"),
        "output_language": answers.get("output_language", "en"),
        "presupposes": [],
        "slide_target": derive_slide_target(duration_hours, tier),
        # Required Maverx constants — fixed by the challenge contract.
        "didactic_blocks": DIDACTIC_BLOCKS,
        "speaker_notes_fields": SPEAKER_NOTES_FIELDS,
        "prebite_required": True,
        "postbite_required": True,
        "cost_tracking_required": True,
        "slide_confidence_required": True,
        "iterative_confirmation_required": True,
    }
