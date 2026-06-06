"""Conversational CLI intake loop."""

import json
from pathlib import Path
from typing import Callable

from intake.parser import (
    coerce_knowledge_level,
    parse_duration,
    parse_level,
    parse_outline_path,
    parse_output_language,
    parse_tier,
)
from intake.validator import validate_field

DRAFT_PATH = Path("intake_draft.json")
FOLLOW_UPS = {
    "topic": "Please describe the specific skill or process, e.g. 'Excel pivot tables for finance analysts'.",
    "audience": "Please name the role, department, or daily context, e.g. 'junior marketing analysts who report campaign performance'.",
    "primary_objective": "Please complete: By the end of this session, participants will be able to...",
    "presupposes": "For Level 2 or 3, list 3-5 concepts participants should already know.",
}


class IntakeAborted(Exception):
    """Raised after repeated invalid input has been saved as a draft."""


def collect_intake(resume: bool = False, input_fn: Callable[[str], str] = input) -> dict:
    data = _load_draft() if resume else {}
    questions = [
        ("tier", "Which tier are you building?\n1 = Single training\n2 = Multi-level track\n3 = Certification programme\n> ", parse_tier),
        ("topic", "What is the topic or skill to be trained?\n> ", _text),
        ("audience", "Who is the target audience?\n> ", _text),
        ("knowledge_level", "What is the knowledge level of participants? (beginner, intermediate, advanced)\n> ", coerce_knowledge_level),
        ("duration_hours", "How long is the training?\n> ", parse_duration),
        ("primary_objective", "What is the primary learning objective?\nComplete: By the end of this session, participants will be able to...\n> ", _text),
        (
            "outline_path",
            "How do you want to create the training outline?\n1 = I will provide my own outline\n2 = Let the system research/propose an outline with me\n> ",
            parse_outline_path,
        ),
        (
            "output_language",
            "What output language do you need?\n1 = English\n2 = Dutch\n3 = Bilingual Dutch + English\n> ",
            parse_output_language,
        ),
        ("level", "Which level are we building?\n1 = Essentials\n2 = Advanced\n3 = Expert\n> ", parse_level),
    ]

    for key, prompt, parser in questions:
        _ask_field(data, key, prompt, parser, input_fn)

    if data["level"] in (2, 3):
        _ask_field(
            data,
            "presupposes",
            "What concepts from the previous level should participants already know? List 3-5, separated by commas.\n> ",
            _parse_concepts,
            input_fn,
        )
    else:
        data["presupposes"] = []
    return data


def _ask_field(data: dict, key: str, prompt: str, parser: Callable, input_fn: Callable[[str], str]) -> None:
    if key in data and not validate_field(key, data[key], data):
        print(f"[RESUME] Keeping valid {key}.")
        return

    for attempt in range(3):
        raw = input_fn(prompt if attempt == 0 else f"{FOLLOW_UPS.get(key, 'Please try again.')}\n> ")
        try:
            value = parser(raw)
            issues = validate_field(key, value, {**data, key: value})
        except ValueError as exc:
            issues = [str(exc)]
            value = raw
        data[key] = value
        if not issues:
            return
        print(f"[INVALID] {key}: {' '.join(issues)}")

    _save_draft(data)
    raise IntakeAborted(f"Three invalid attempts for {key}. Partial answers saved to {DRAFT_PATH}.")


def _load_draft() -> dict:
    if not DRAFT_PATH.exists():
        return {}
    try:
        data = json.loads(DRAFT_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save_draft(data: dict) -> None:
    DRAFT_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _text(raw: str) -> str:
    return raw.strip()


def _parse_concepts(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]
