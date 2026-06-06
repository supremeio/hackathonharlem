"""
Intake engine.

Responsibilities (all required by the brief):
  1. Ask the 5 mandatory questions.
  2. Detect vague answers and ask targeted follow-ups instead of guessing.
  3. Refuse to hand off to generation until intake is sufficiently complete.

The engine is UI-agnostic: the Streamlit app and the CLI both drive the same
``IntakeState``. Vagueness detection is heuristic-first (works with no API key)
and can optionally be sharpened by the LLM.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .config import INTAKE_QUESTIONS, duration_to_minutes

_LEVELS = {"beginner", "intermediate", "advanced"}
_LEVEL_HINTS = {
    "beginner": "beginner", "novice": "beginner", "new": "beginner",
    "none": "beginner", "no prior": "beginner", "basic": "beginner",
    "intermediate": "intermediate", "some": "intermediate", "medium": "intermediate",
    "advanced": "advanced", "expert": "advanced", "experienced": "advanced",
}
_VAGUE_WORDS = {
    "stuff", "things", "everyone", "everybody", "people", "anyone", "general",
    "various", "etc", "whatever", "all", "some things", "misc",
}


@dataclass
class IntakeState:
    answers: Dict[str, str] = field(default_factory=dict)
    transcript: List[Dict[str, str]] = field(default_factory=list)  # {role, text}

    # ---- public API ---------------------------------------------------- #
    def next_key(self) -> Optional[str]:
        """Key of the next unanswered required question, or None when all set."""
        for q in INTAKE_QUESTIONS:
            if q["key"] not in self.answers:
                return q["key"]
        return None

    def question_for(self, key: str) -> str:
        return next(q["question"] for q in INTAKE_QUESTIONS if q["key"] == key)

    def missing(self) -> List[str]:
        return [q["key"] for q in INTAKE_QUESTIONS if q["key"] not in self.answers]

    def record(self, key: str, answer: str) -> Tuple[bool, Optional[str]]:
        """
        Validate and (if acceptable) store an answer.

        Returns ``(accepted, followup)``:
          - accepted=True  → stored; followup is None
          - accepted=False → not stored; followup is the question to ask next
        """
        answer = (answer or "").strip()
        self.transcript.append({"role": "user", "key": key, "text": answer})
        ok, followup = validate_answer(key, answer)
        if ok:
            self.answers[key] = normalize_answer(key, answer)
        if followup:
            self.transcript.append({"role": "assistant", "key": key, "text": followup})
        return ok, followup

    def is_complete(self) -> bool:
        if self.missing():
            return False
        return all(validate_answer(k, v)[0] for k, v in self.answers.items())

    def summary(self) -> Dict[str, str]:
        return dict(self.answers)


# --------------------------------------------------------------------------- #
# Validation / vagueness heuristics
# --------------------------------------------------------------------------- #
def _looks_vague(text: str) -> bool:
    t = text.lower().strip()
    if len(t) < 3:
        return True
    words = [w for w in t.replace(",", " ").split() if w]
    if len(words) == 1 and t in _VAGUE_WORDS:
        return True
    if t in _VAGUE_WORDS:
        return True
    return False


def validate_answer(key: str, answer: str) -> Tuple[bool, Optional[str]]:
    """Heuristic gate per field. Returns (ok, followup_question)."""
    a = (answer or "").strip()
    if not a:
        return False, "I didn't catch that — could you give me a short answer?"

    if key == "topic":
        if _looks_vague(a) or len(a.split()) < 2 and a.lower() in _VAGUE_WORDS:
            return False, (
                "That's a little broad. Which specific skill or topic should this "
                "training cover? (e.g. 'prompt engineering for marketing copy', "
                "not just 'AI')"
            )
        return True, None

    if key == "audience":
        if _looks_vague(a):
            return False, (
                "Who exactly is in the room? Name the team, role or function "
                "(e.g. 'the marketing team', 'finance managers') — 'everyone' is "
                "too broad to set the right tone."
            )
        return True, None

    if key == "level":
        mapped = _map_level(a)
        if mapped is None:
            return False, (
                "What's their knowledge level — beginner, intermediate, or "
                "advanced? You can describe it (e.g. 'no prior experience')."
            )
        return True, None

    if key == "duration":
        mins = duration_to_minutes(a)
        if mins <= 0 or not any(c.isdigit() for c in a) and "day" not in a.lower():
            return False, (
                "How long is the session? Give me a duration like '2 hours', "
                "'90 minutes', or 'half a day'."
            )
        if mins < 30:
            return False, (
                f"{mins} minutes is very short for a full didactic arc. Could you "
                "confirm the duration? Most trainings run 60 minutes or more."
            )
        return True, None

    if key == "objective":
        if _looks_vague(a) or len(a.split()) < 3:
            return False, (
                "What should participants be able to DO after the session? Phrase "
                "it as a capability (e.g. 'write effective prompts for campaign "
                "briefs'), not just the topic name."
            )
        return True, None

    return True, None


def normalize_answer(key: str, answer: str) -> str:
    if key == "level":
        return _map_level(answer) or answer.strip()
    return answer.strip()


def _map_level(text: str) -> Optional[str]:
    t = text.lower().strip()
    if t in _LEVELS:
        return t
    for hint, lvl in _LEVEL_HINTS.items():
        if hint in t:
            return lvl
    return None


# --------------------------------------------------------------------------- #
# Optional LLM-assisted follow-up (used only when a key is available).
# --------------------------------------------------------------------------- #
def llm_followup(key: str, answer: str, llm) -> Optional[str]:
    """
    Ask the model whether an answer that PASSED heuristics is still too thin,
    and if so propose one sharpening follow-up. Returns None if it's fine.
    """
    if llm is None or not llm.available:
        return None
    q = next(x["question"] for x in INTAKE_QUESTIONS if x["key"] == key)
    prompt = (
        "You are running the intake for a training-design assistant. The "
        f"question was: \"{q}\". The trainer answered: \"{answer}\". "
        "If this answer is specific enough to design a high-quality training, "
        "reply with exactly OK. Otherwise reply with ONE short follow-up "
        "question (no preamble) that would make it specific enough."
    )
    try:
        out = llm.complete(prompt, max_tokens=120, temperature=0.2).strip()
    except Exception:
        return None
    if out.upper().startswith("OK") or len(out) < 5:
        return None
    return out
