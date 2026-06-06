"""Validation gate and Training Readiness Score."""

from typing import Any

DIDACTIC_BLOCKS = ["kick-off", "theory", "example", "exercise", "wrap-up"]
SPEAKER_NOTES_FIELDS = [
    "aim",
    "time",
    "instructions",
    "reflective_question",
    "debrief",
]

VAGUE_TOPICS = {
    "excel",
    "word",
    "safety",
    "hr",
    "leadership",
    "compliance",
    "it",
    "software",
    "ai",
    "power bi",
    "communication",
}
VAGUE_AUDIENCES = {"employees", "staff", "people", "workers", "team", "everyone", "users"}
ACTION_VERBS = {
    "demonstrate",
    "apply",
    "build",
    "identify",
    "analyze",
    "analyse",
    "create",
    "explain",
    "design",
    "use",
    "evaluate",
    "implement",
}
SCORE_WEIGHTS = {
    "tier": 5,
    "topic": 15,
    "audience": 15,
    "knowledge_level": 10,
    "duration_hours": 10,
    "primary_objective": 25,
    "level": 10,
    "presupposes": 10,
}


def validate_field(key: str, value: Any, data: dict | None = None) -> list[str]:
    data = data or {}
    issues: list[str] = []

    if key == "tier" and (type(value) is not int or value not in (1, 2, 3)):
        issues.append("Must be 1, 2, or 3.")
    elif key == "topic":
        text = _text(value)
        if not text:
            issues.append("Required.")
        elif text.lower() in VAGUE_TOPICS:
            issues.append("Too vague. Describe the specific skill or process.")
    elif key == "audience":
        text = _text(value)
        if not text:
            issues.append("Required.")
        elif text.lower() in VAGUE_AUDIENCES:
            issues.append("Too vague. Name the role, department, or daily context.")
    elif key == "knowledge_level" and value not in ("beginner", "intermediate", "advanced"):
        issues.append("Must be beginner, intermediate, or advanced.")
    elif key == "outline_path" and value not in ("trainer_supplied", "research_assisted"):
        issues.append("Must be trainer_supplied or research_assisted.")
    elif key == "output_language" and value not in ("en", "nl", "bilingual"):
        issues.append("Must be en, nl, or bilingual.")
    elif key == "duration_hours":
        if type(value) not in (int, float) or isinstance(value, bool) or value <= 0:
            issues.append("Must be a positive number of hours.")
        elif value > 40:
            issues.append("Must not exceed 40 hours.")
    elif key == "primary_objective":
        text = _text(value)
        if len(text) < 20:
            issues.append("Must be at least 20 characters.")
        words = set(_words(text))
        if not words.intersection(ACTION_VERBS):
            issues.append("Must contain a measurable action verb.")
    elif key == "level" and (type(value) is not int or value not in (1, 2, 3)):
        issues.append("Must be 1, 2, or 3.")
    elif key == "presupposes":
        level = data.get("level")
        if not isinstance(value, list):
            issues.append("Must be an array.")
        elif any(not _text(item) for item in value):
            issues.append("Concepts must not be empty.")
        elif level in (2, 3) and not 3 <= len(value) <= 5:
            issues.append("Level 2 or 3 requires 3-5 prior concepts.")
        elif level == 1 and value:
            issues.append("Level 1 must not presuppose previous concepts.")
    elif key == "slide_target" and (type(value) is not int or value <= 0):
        issues.append("Must be a positive integer.")
    elif key == "didactic_blocks" and value != DIDACTIC_BLOCKS:
        issues.append(f"Must exactly equal {DIDACTIC_BLOCKS}.")
    elif key == "speaker_notes_fields" and value != SPEAKER_NOTES_FIELDS:
        issues.append(f"Must exactly equal {SPEAKER_NOTES_FIELDS}.")
    elif key == "prebite_required" and value is not True:
        issues.append("Must be true.")
    elif key == "postbite_required" and value is not True:
        issues.append("Must be true.")
    elif key == "cost_tracking_required" and value is not True:
        issues.append("Must be true.")
    elif key == "slide_confidence_required" and value is not True:
        issues.append("Must be true.")
    elif key == "iterative_confirmation_required" and value is not True:
        issues.append("Must be true.")
    return issues


def validate_intake(data: dict) -> list[str]:
    fields = [
        *SCORE_WEIGHTS,
        "outline_path",
        "output_language",
        "slide_target",
        "didactic_blocks",
        "speaker_notes_fields",
        "prebite_required",
        "postbite_required",
        "cost_tracking_required",
        "slide_confidence_required",
        "iterative_confirmation_required",
    ]
    issues: list[str] = []
    for key in fields:
        if key not in data:
            issues.append(f"{key}: Required.")
            continue
        issues.extend(f"{key}: {issue}" for issue in validate_field(key, data[key], data))
    return issues


def score_intake(data: dict) -> tuple[int, dict]:
    breakdown = {}
    total = 0
    for key, weight in SCORE_WEIGHTS.items():
        points = weight if key in data and not validate_field(key, data[key], data) else 0
        breakdown[key] = {"score": points, "max": weight}
        total += points
    return total, breakdown


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _words(value: str) -> list[str]:
    return [word.strip(".,:;!?").lower() for word in value.split()]
