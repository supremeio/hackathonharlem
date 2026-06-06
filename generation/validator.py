"""Validation for deterministic Person B outputs."""

import json
from pathlib import Path
from typing import Any

BLOCK_ORDER = ["kick-off", "theory", "example", "exercise", "wrap-up"]
NOTE_FIELDS = [
    "aim",
    "time",
    "instructions",
    "reflective_question",
    "debrief",
    "key_discussion_points",
    "link_to_reality",
]


class GenerationValidationError(ValueError):
    """Raised when generated content violates the Person B contract."""


def load_allowed_slide_types(schema_path: str | Path | None = None) -> set[str]:
    path = Path(schema_path) if schema_path else Path(__file__).parents[1] / "schemas" / "slides_schema.json"
    schema = json.loads(path.read_text(encoding="utf-8"))
    return set(schema["items"]["properties"]["slide_type"]["enum"])


def validate_deck(deck: dict, intake: dict, level: int) -> list[str]:
    issues = []
    required_top = {
        "schema_version",
        "generation_mode",
        "output_language",
        "model_name",
        "cost_tracking",
        "slides",
    }
    issues.extend(_missing(deck, required_top, "deck"))
    slides = deck.get("slides")
    if not isinstance(slides, list):
        return issues + ["deck.slides: Must be a list."]
    if len(slides) != 20:
        issues.append(f"deck.slides: Expected exactly 20 slides, got {len(slides)}.")

    allowed = load_allowed_slide_types()
    blocks = []
    for expected_number, slide in enumerate(slides, start=1):
        prefix = f"slide {expected_number}"
        if not isinstance(slide, dict):
            issues.append(f"{prefix}: Must be an object.")
            continue
        issues.extend(_missing(slide, {
            "slide_number", "slide_type", "block", "level", "title", "body", "table",
            "visual_suggestion", "confidence_score", "confidence_reason", "speaker_notes",
        }, prefix))
        if slide.get("slide_number") != expected_number:
            issues.append(f"{prefix}.slide_number: Must equal {expected_number}.")
        if slide.get("slide_type") not in allowed:
            issues.append(f"{prefix}.slide_type: Not allowed by schemas/slides_schema.json.")
        if slide.get("level") != level:
            issues.append(f"{prefix}.level: Must equal {level}.")
        blocks.append(slide.get("block"))
        for key in ("title", "visual_suggestion", "confidence_reason"):
            if not _non_empty_string(slide.get(key)):
                issues.append(f"{prefix}.{key}: Must be non-empty.")
        body = slide.get("body")
        if not isinstance(body, list) or not body or any(not _non_empty_string(item) for item in body):
            issues.append(f"{prefix}.body: Must be a non-empty list of strings.")
        if slide.get("table") is not None and not isinstance(slide.get("table"), dict):
            issues.append(f"{prefix}.table: Must be null or an object.")
        score = slide.get("confidence_score")
        if not isinstance(score, (int, float)) or isinstance(score, bool) or not 0 <= score <= 1:
            issues.append(f"{prefix}.confidence_score: Must be between 0 and 1.")
        issues.extend(_validate_notes(slide.get("speaker_notes"), prefix))

    if _condensed(blocks) != BLOCK_ORDER:
        issues.append(f"deck.slides: Blocks must be contiguous and ordered as {BLOCK_ORDER}.")
    recap_count = sum(slide.get("slide_type") == "mentimeter_recap" for slide in slides if isinstance(slide, dict))
    if level == 1 and recap_count:
        issues.append("deck.slides: Level 1 must not contain mentimeter_recap.")
    if level in (2, 3) and recap_count != 1:
        issues.append(f"deck.slides: Level {level} requires exactly one mentimeter_recap.")

    searchable = json.dumps(slides, ensure_ascii=False).lower()
    if level == 2 and "level 1" not in searchable:
        issues.append("deck.slides: Level 2 must explicitly reference Level 1 concepts.")
    if level == 3 and ("level 1" not in searchable or "level 2" not in searchable):
        issues.append("deck.slides: Level 3 must explicitly reference Level 1 and Level 2 concepts.")
    cost = deck.get("cost_tracking")
    if not isinstance(cost, dict) or _missing(cost, {
        "model_name", "input_tokens_estimate", "output_tokens_estimate", "estimated_cost_eur"
    }, "cost_tracking"):
        issues.append("cost_tracking: Missing required fields.")
    return issues


def validate_artifacts(prebite: dict, postbite: dict, dataset: dict, intake: dict, level: int) -> list[str]:
    issues = []
    issues.extend(_validate_artifact(prebite, {
        "title", "output_language", "estimated_minutes", "purpose", "content", "reflection_questions"
    }, "prebite"))
    issues.extend(_validate_artifact(postbite, {
        "title", "output_language", "estimated_minutes", "summary", "reflection_questions",
        "assignment", "next_level_bridge"
    }, "postbite"))
    issues.extend(_validate_artifact(dataset, {
        "title", "scenario", "level", "columns", "sample_rows", "expected_outcome"
    }, "dataset"))
    if prebite.get("output_language") != intake.get("output_language"):
        issues.append("prebite.output_language: Must match intake.")
    if postbite.get("output_language") != intake.get("output_language"):
        issues.append("postbite.output_language: Must match intake.")
    if dataset.get("level") != level:
        issues.append(f"dataset.level: Must equal {level}.")
    columns = dataset.get("columns")
    if not isinstance(columns, list) or not columns:
        issues.append("dataset.columns: Must be a non-empty list.")
    else:
        for index, column in enumerate(columns, start=1):
            if not isinstance(column, dict) or _missing(
                column, {"name", "type", "description", "adjustable"}, f"dataset.columns[{index}]"
            ):
                issues.append(f"dataset.columns[{index}]: Invalid column.")
    return issues


def ensure_valid(issues: list[str]) -> None:
    if issues:
        raise GenerationValidationError("\n".join(issues))


def _validate_notes(notes: Any, prefix: str) -> list[str]:
    if not isinstance(notes, dict):
        return [f"{prefix}.speaker_notes: Must be an object."]
    issues = []
    for key in NOTE_FIELDS:
        value = notes.get(key)
        if key == "key_discussion_points":
            if not isinstance(value, list) or not value or any(not _non_empty_string(item) for item in value):
                issues.append(f"{prefix}.speaker_notes.{key}: Must be a non-empty list.")
        elif not _non_empty_string(value):
            issues.append(f"{prefix}.speaker_notes.{key}: Must be non-empty.")
    return issues


def _validate_artifact(data: Any, fields: set[str], name: str) -> list[str]:
    if not isinstance(data, dict):
        return [f"{name}: Must be an object."]
    issues = _missing(data, fields, name)
    for key, value in data.items():
        if key in ("estimated_minutes", "level", "sample_rows", "columns", "output_language"):
            continue
        if isinstance(value, str) and not value.strip():
            issues.append(f"{name}.{key}: Must be non-empty.")
        if isinstance(value, list) and key != "sample_rows" and not value:
            issues.append(f"{name}.{key}: Must be non-empty.")
    return issues


def _missing(data: dict, fields: set[str], prefix: str) -> list[str]:
    return [f"{prefix}.{field}: Required." for field in sorted(fields - set(data))]


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _condensed(values: list[Any]) -> list[Any]:
    result = []
    for value in values:
        if not result or result[-1] != value:
            result.append(value)
    return result
