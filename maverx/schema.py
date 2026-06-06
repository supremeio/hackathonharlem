"""
Typed data model for a generated training.

The planner (LLM or offline fallback) produces a ``Training`` instance; the deck
and bite generators consume it. Keeping a single validated schema between the
"thinking" and "rendering" halves is what makes the pipeline robust to edge
cases and easy for someone else to extend.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


@dataclass
class SpeakerNotes:
    """The 6 mandatory facilitation fields, present on every content slide."""
    aim: str = ""
    time: str = ""
    instructions: str = ""
    discussion_points: List[str] = field(default_factory=list)
    link_to_reality: str = ""
    reflective_question: str = ""
    debrief: str = ""

    def render(self) -> str:
        dp = "\n".join(f"   - {p}" for p in self.discussion_points) or "   - (none)"
        return (
            f"AIM\n{self.aim}\n\n"
            f"TIME\n{self.time}\n\n"
            f"INSTRUCTIONS\n{self.instructions}\n\n"
            f"KEY DISCUSSION POINTS\n{dp}\n\n"
            f"LINK TO REALITY\n{self.link_to_reality}\n\n"
            f"REFLECTIVE QUESTION\n{self.reflective_question}\n\n"
            f"DEBRIEF & SUMMARY\n{self.debrief}\n"
        )


@dataclass
class AboutSession:
    learning_objectives: List[str] = field(default_factory=list)
    learning_outcomes: List[str] = field(default_factory=list)
    target_group: str = ""
    good_to_know: List[str] = field(default_factory=list)
    badge: str = "ALL PROFESSIONALS WELCOME"


@dataclass
class TheoryBlock:
    title: str = ""
    definition: str = ""
    points: List[str] = field(default_factory=list)
    statement: str = ""          # the big indigo one-liner
    notes: SpeakerNotes = field(default_factory=SpeakerNotes)


@dataclass
class ExampleBlock:
    title: str = ""
    scenario: str = ""
    points: List[str] = field(default_factory=list)
    notes: SpeakerNotes = field(default_factory=SpeakerNotes)


@dataclass
class ExerciseBlock:
    title: str = ""
    fmt: str = "group"           # individual | pair | group
    duration_min: int = 15
    steps: List[str] = field(default_factory=list)
    debrief_questions: List[str] = field(default_factory=list)
    notes: SpeakerNotes = field(default_factory=SpeakerNotes)


@dataclass
class Module:
    name: str = ""
    minutes: int = 30
    theory: TheoryBlock = field(default_factory=TheoryBlock)
    example: ExampleBlock = field(default_factory=ExampleBlock)
    exercise: ExerciseBlock = field(default_factory=ExerciseBlock)


@dataclass
class WrapUp:
    takeaways: List[str] = field(default_factory=list)
    whats_next: List[str] = field(default_factory=list)
    reflection: List[str] = field(default_factory=list)


@dataclass
class Bite:
    title: str = ""
    intro: str = ""
    sections: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class TimetableRow:
    segment: str
    minutes: int
    activity: str


@dataclass
class Training:
    # --- intake echo ---
    topic: str = ""
    audience: str = ""
    level: str = ""
    duration_text: str = ""
    duration_min: int = 120
    objective: str = ""

    # --- generated structure ---
    title: str = ""
    subtitle: str = ""
    about: AboutSession = field(default_factory=AboutSession)
    kickoff_goals: List[str] = field(default_factory=list)
    agenda: List[str] = field(default_factory=list)
    modules: List[Module] = field(default_factory=list)
    wrapup: WrapUp = field(default_factory=WrapUp)
    trainer_timetable: List[TimetableRow] = field(default_factory=list)
    learner_timetable: List[str] = field(default_factory=list)

    # --- companion documents ---
    prebite: Bite = field(default_factory=Bite)
    postbite: Bite = field(default_factory=Bite)

    # --- provenance ---
    generated_by: str = "offline-template"   # or the model id
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
