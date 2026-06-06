"""
Planner: intake answers -> validated ``Training``.

Two interchangeable engines behind one ``plan_training`` call:

  * LLM engine  — when an OpenRouter key is present. Prompts the model for a
    single JSON object following the Maverx didactic model, then maps it onto
    the typed schema. Missing fields are healed from the offline defaults, so a
    partial or imperfect model response still yields a complete, valid deck.

  * Offline engine — deterministic, no network. Produces a coherent, on-brand
    training from the intake alone, so the system always runs in a demo and is
    trivially testable.

Both engines share the structural scaffolding (module count, timetables) so the
didactic arc and timing are consistent regardless of which one ran.
"""

from __future__ import annotations

import json
from typing import List, Optional

from .config import duration_to_minutes
from .llm import OpenRouterClient
from .schema import (
    AboutSession, Bite, ExampleBlock, ExerciseBlock, Module, SpeakerNotes,
    TheoryBlock, TimetableRow, Training, WrapUp,
)


# --------------------------------------------------------------------------- #
# Structural helpers (shared by both engines)
# --------------------------------------------------------------------------- #
def module_count(duration_min: int) -> int:
    n = round((duration_min - 30) / 40)
    return max(1, min(6, int(n)))


def build_timetables(tr: Training) -> None:
    """Fill trainer + learner timetables so segment minutes sum to duration."""
    total = tr.duration_min
    n = len(tr.modules)
    # Fixed framing segments (scaled lightly for short/long sessions).
    kick = max(5, round(total * 0.06))
    wrap = max(10, round(total * 0.10))
    framing = kick + wrap
    per_module = max(20, (total - framing) // max(1, n))

    rows: List[TimetableRow] = [
        TimetableRow("Kick-off & learning goals", kick, "Welcome, agenda, objectives"),
    ]
    for m in tr.modules:
        m.minutes = per_module
        theory_t = max(5, round(per_module * 0.4))
        example_t = max(3, round(per_module * 0.25))
        ex_t = max(5, per_module - theory_t - example_t)
        m.exercise.duration_min = ex_t
        rows.append(TimetableRow(f"{m.name} — theory & example", theory_t + example_t,
                                 "Introduce concept, show it in practice"))
        rows.append(TimetableRow(f"{m.name} — exercise & debrief", ex_t,
                                 f"{m.exercise.fmt.title()} work, then debrief"))
    rows.append(TimetableRow("Wrap-up, key takeaways & next steps", wrap,
                             "Reflection, takeaways, what's next"))

    # Reconcile rounding drift onto the wrap-up row.
    drift = total - sum(r.minutes for r in rows)
    rows[-1] = TimetableRow(rows[-1].segment, max(5, rows[-1].minutes + drift),
                            rows[-1].activity)
    tr.trainer_timetable = rows

    tr.learner_timetable = (
        ["Welcome — why this matters & what you'll be able to do"]
        + [f"{m.name} — learn it, see it, try it" for m in tr.modules]
        + ["Commit — your takeaways and next step"]
    )


# --------------------------------------------------------------------------- #
# Public entry point
# --------------------------------------------------------------------------- #
def plan_training(answers: dict, llm: Optional[OpenRouterClient] = None,
                  progress=None) -> Training:
    def _say(msg):
        if progress:
            progress(msg)

    tr = _base_training(answers)

    if llm is not None and llm.available:
        try:
            _say("Designing the training with the model…")
            data = _llm_plan(tr, llm)
            _apply_llm(tr, data)
            tr.generated_by = llm.model
        except Exception as e:  # graceful degradation — never crash the demo
            _say(f"Model planning failed ({e}); using offline template.")
            _offline_plan(tr)
            tr.generated_by = f"offline-template (LLM error: {e})"
    else:
        _say("No API key — generating with the offline template engine…")
        _offline_plan(tr)

    build_timetables(tr)
    _ensure_complete(tr)
    return tr


def _base_training(answers: dict) -> Training:
    dtext = answers.get("duration", "2 hours")
    tr = Training(
        topic=answers.get("topic", "").strip(),
        audience=answers.get("audience", "").strip(),
        level=answers.get("level", "intermediate").strip(),
        duration_text=dtext,
        duration_min=duration_to_minutes(dtext),
        objective=answers.get("objective", "").strip(),
    )
    return tr


# --------------------------------------------------------------------------- #
# LLM engine
# --------------------------------------------------------------------------- #
_SYSTEM = (
    "You are an expert instructional designer for Maverx, a Dutch training "
    "agency. You design corporate trainings that strictly follow a didactic "
    "arc: Kick-off -> Theory -> Example -> Exercise -> Wrap-up. You write "
    "tight, concrete, audience-appropriate content — never filler. You always "
    "return a single valid JSON object and nothing else."
)


def _llm_plan(tr: Training, llm: OpenRouterClient) -> dict:
    n = module_count(tr.duration_min)
    schema_hint = {
        "title": "Proper-Case training title",
        "subtitle": "one lower-case line",
        "about": {
            "learning_objectives": ["3-5 verb-led objectives"],
            "learning_outcomes": ["3-4 outcomes (what changes for them)"],
            "target_group": "one sentence describing who this is for",
            "good_to_know": ["2-4 practical notes about format/approach"],
        },
        "kickoff_goals": ["3-4 goals stated for the kick-off"],
        "agenda": [f"{n} agenda lines, one per module, 'Topic — short descriptor'"],
        "modules": [
            {
                "name": "module/topic name",
                "theory": {
                    "title": "slide title",
                    "definition": "1-2 sentence definition/explanation",
                    "points": ["3-4 core points"],
                    "statement": "one punchy indigo one-liner",
                    "notes": "SPEAKER_NOTES_OBJECT",
                },
                "example": {
                    "title": "slide title",
                    "scenario": "a concrete, recognizable illustration (2-3 sentences)",
                    "points": ["2-3 takeaways from the example"],
                    "notes": "SPEAKER_NOTES_OBJECT",
                },
                "exercise": {
                    "title": "slide title",
                    "fmt": "individual | pair | group",
                    "duration_min": 15,
                    "steps": ["3-5 numbered actionable steps"],
                    "debrief_questions": ["2-3 debrief questions"],
                    "notes": "SPEAKER_NOTES_OBJECT",
                },
            }
        ],
        "wrapup": {
            "takeaways": ["3-5 key takeaways"],
            "whats_next": ["2-3 next steps"],
            "reflection": ["1-2 reflection prompts"],
        },
        "prebite": {
            "title": "title",
            "intro": "1-2 sentences",
            "reading": ["1-3 prep items: article/video to read or watch"],
            "to_install": ["software/accounts to set up, or empty"],
            "reflection": ["1-2 pre-session reflection questions"],
        },
        "postbite": {
            "title": "title",
            "intro": "1-2 sentences",
            "reflection": ["1-2 post-session reflection questions"],
            "assignment": "one concrete follow-up assignment",
            "further_reading": ["1-3 resources"],
        },
    }
    speaker_notes_spec = {
        "aim": "one clear sentence on the slide's purpose",
        "time": "short estimate e.g. '5 min'",
        "instructions": "trainer-ready, conversational, what to say and do, step by step",
        "discussion_points": ["the 3-4 things that must land"],
        "link_to_reality": "a concrete story or analogy that makes it stick",
        "reflective_question": "one question to pose to learners",
        "debrief": "one punchy closing line",
    }

    prompt = f"""Design ONE complete Maverx training.

INTAKE
- Topic / skill: {tr.topic}
- Audience: {tr.audience}
- Knowledge level: {tr.level}
- Duration: {tr.duration_text} (~{tr.duration_min} minutes)
- Primary learning objective: {tr.objective}

REQUIREMENTS
- Produce exactly {n} module(s), sized for the duration.
- Every module MUST have theory, example and exercise blocks.
- Every theory/example/exercise block MUST include a "notes" object with ALL of
  these fields: aim, time, instructions, discussion_points (array),
  link_to_reality, reflective_question, debrief.
- Content must match the audience ({tr.audience}) and level ({tr.level}).
- Be concrete and specific to the topic. No "Lorem ipsum", no placeholders.

Return a single JSON object with EXACTLY this shape (replace every
SPEAKER_NOTES_OBJECT with an object shaped like SPEAKER_NOTES_SPEC):

JSON_SHAPE = {json.dumps(schema_hint)}

SPEAKER_NOTES_SPEC = {json.dumps(speaker_notes_spec)}
"""
    return llm.complete_json(prompt, system=_SYSTEM, temperature=0.55)


def _notes_from(d: dict) -> SpeakerNotes:
    d = d or {}
    dp = d.get("discussion_points") or d.get("key_discussion_points") or []
    if isinstance(dp, str):
        dp = [dp]
    return SpeakerNotes(
        aim=str(d.get("aim", "")).strip(),
        time=str(d.get("time", "")).strip(),
        instructions=str(d.get("instructions", "")).strip(),
        discussion_points=[str(x) for x in dp],
        link_to_reality=str(d.get("link_to_reality", "")).strip(),
        reflective_question=str(d.get("reflective_question", "")).strip(),
        debrief=str(d.get("debrief", "")).strip(),
    )


def _apply_llm(tr: Training, data: dict) -> None:
    tr.title = (data.get("title") or "").strip() or _default_title(tr)
    tr.subtitle = (data.get("subtitle") or "").strip() or _default_subtitle(tr)

    ab = data.get("about", {}) or {}
    tr.about = AboutSession(
        learning_objectives=_as_list(ab.get("learning_objectives")),
        learning_outcomes=_as_list(ab.get("learning_outcomes")),
        target_group=str(ab.get("target_group", "")).strip(),
        good_to_know=_as_list(ab.get("good_to_know")),
    )
    tr.kickoff_goals = _as_list(data.get("kickoff_goals"))
    tr.agenda = _as_list(data.get("agenda"))

    mods = []
    for m in data.get("modules", []) or []:
        th = m.get("theory", {}) or {}
        ex = m.get("example", {}) or {}
        xr = m.get("exercise", {}) or {}
        mods.append(Module(
            name=str(m.get("name", "")).strip(),
            theory=TheoryBlock(
                title=str(th.get("title", "")).strip(),
                definition=str(th.get("definition", "")).strip(),
                points=_as_list(th.get("points")),
                statement=str(th.get("statement", "")).strip(),
                notes=_notes_from(th.get("notes")),
            ),
            example=ExampleBlock(
                title=str(ex.get("title", "")).strip(),
                scenario=str(ex.get("scenario", "")).strip(),
                points=_as_list(ex.get("points")),
                notes=_notes_from(ex.get("notes")),
            ),
            exercise=ExerciseBlock(
                title=str(xr.get("title", "")).strip(),
                fmt=str(xr.get("fmt", "group")).strip() or "group",
                duration_min=int(xr.get("duration_min", 15) or 15),
                steps=_as_list(xr.get("steps")),
                debrief_questions=_as_list(xr.get("debrief_questions")),
                notes=_notes_from(xr.get("notes")),
            ),
        ))
    tr.modules = mods

    wu = data.get("wrapup", {}) or {}
    tr.wrapup = WrapUp(
        takeaways=_as_list(wu.get("takeaways")),
        whats_next=_as_list(wu.get("whats_next")),
        reflection=_as_list(wu.get("reflection")),
    )

    pb = data.get("prebite", {}) or {}
    tr.prebite = Bite(
        title=str(pb.get("title", "")).strip() or f"Before we start: {tr.topic}",
        intro=str(pb.get("intro", "")).strip(),
        sections={
            "Read / watch": _as_list(pb.get("reading")),
            "Set up": _as_list(pb.get("to_install")),
            "Reflect": _as_list(pb.get("reflection")),
        },
    )
    sb = data.get("postbite", {}) or {}
    tr.postbite = Bite(
        title=str(sb.get("title", "")).strip() or f"After the session: {tr.topic}",
        intro=str(sb.get("intro", "")).strip(),
        sections={
            "Reflect": _as_list(sb.get("reflection")),
            "Assignment": _as_list(sb.get("assignment")),
            "Go further": _as_list(sb.get("further_reading")),
        },
    )


# --------------------------------------------------------------------------- #
# Offline engine — deterministic, on-brand content from the intake
# --------------------------------------------------------------------------- #
def _offline_plan(tr: Training) -> None:
    n = module_count(tr.duration_min)
    tr.title = _default_title(tr)
    tr.subtitle = _default_subtitle(tr)

    tr.about = AboutSession(
        learning_objectives=[
            f"Understand the core ideas behind {tr.topic}.",
            f"Recognise where {tr.topic} applies in your own work.",
            f"Apply {tr.topic} to a realistic task with guidance.",
            f"Judge when and how to use {tr.topic} responsibly.",
        ],
        learning_outcomes=[
            f"Be able to {tr.objective.rstrip('.').lower()}.",
            f"Leave with a concrete first step for using {tr.topic}.",
            "Build confidence through hands-on practice, not theory alone.",
        ],
        target_group=(f"{tr.audience} — pitched at a {tr.level} level. "
                      "No specialist background assumed beyond that."),
        good_to_know=[
            "Practical and hands-on — built around real use cases.",
            "A mix of short concepts, demonstrations and exercises.",
            "You leave with something you can apply immediately.",
        ],
    )
    tr.kickoff_goals = [
        f"Set out what you'll be able to do with {tr.topic} by the end.",
        "Agree the agenda and how we'll work together today.",
        "Surface what you already know and what you want to get out of it.",
    ]

    subtopics = _offline_subtopics(tr.topic, n)
    tr.agenda = [f"{s} — {hint}" for s, hint in subtopics]
    tr.modules = [_offline_module(tr, name) for name, _ in subtopics]

    tr.wrapup = WrapUp(
        takeaways=[f"{m.name}: one thing to remember and apply." for m in tr.modules]
        + [f"You can now begin to {tr.objective.rstrip('.').lower()}."],
        whats_next=[
            "Pick one idea from today and try it this week.",
            "Share your result with a colleague to keep momentum.",
            "Note one question to bring to a follow-up session.",
        ],
        reflection=[
            "What is one thing you'll do differently after today?",
            "Where could this help most in your day-to-day work?",
        ],
    )

    tr.prebite = Bite(
        title=f"Before we start: {tr.topic}",
        intro=(f"A short prep so we can spend our time together practising "
               f"{tr.topic} rather than setting up."),
        sections={
            "Read / watch": [
                f"Skim one short introduction to {tr.topic} (10 minutes).",
            ],
            "Set up": [
                "Bring a real task from your own work we can use as a case.",
            ],
            "Reflect": [
                f"Where do you currently spend effort that {tr.topic} might help with?",
            ],
        },
    )
    tr.postbite = Bite(
        title=f"After the session: {tr.topic}",
        intro="Lock in what you learned and turn it into a habit.",
        sections={
            "Reflect": [
                "Which part of today was most useful, and why?",
                f"Where will you apply {tr.topic} first?",
            ],
            "Assignment": [
                f"Apply {tr.topic} to one real task this week and capture the result.",
            ],
            "Go further": [
                f"Find one resource that deepens your understanding of {tr.topic}.",
            ],
        },
    )


def _offline_module(tr: Training, name: str) -> Module:
    return Module(
        name=name,
        theory=TheoryBlock(
            title=name,
            definition=(f"{name} is a key part of {tr.topic}. In short: it is the "
                        "idea that makes the rest of today practical."),
            points=[
                f"What {name.lower()} means in plain terms.",
                f"Why it matters for {tr.audience}.",
                "How to recognise it in your own work.",
            ],
            statement=f"Get {name.lower()} right and the rest follows.",
            notes=SpeakerNotes(
                aim=f"Introduce {name} and why it matters to {tr.audience}.",
                time="8 min",
                instructions=(f"Open by asking what people already associate with "
                              f"{name}. Define it in one line, then walk the three "
                              "points. Keep it concrete — tie each point back to "
                              "their work."),
                discussion_points=[
                    f"A clear definition of {name}.",
                    "Why it matters here, specifically.",
                    "One sign you'd spot it in practice.",
                ],
                link_to_reality=(f"Relate {name} to a familiar moment in the "
                                 f"{tr.audience}'s week so it sticks."),
                reflective_question=f"Where have you already met {name} without naming it?",
                debrief=f"{name} is simpler than it sounds — and useful today.",
            ),
        ),
        example=ExampleBlock(
            title=f"{name} in practice",
            scenario=(f"Picture a typical situation for {tr.audience}: a real task "
                      f"where {name} changes the outcome. Walk through what good "
                      "looks like, step by step."),
            points=[
                "What was done, and why it worked.",
                "The one decision that made the difference.",
            ],
            notes=SpeakerNotes(
                aim=f"Make {name} concrete with a recognisable example.",
                time="5 min",
                instructions=("Narrate the example slowly. Pause at the key "
                              "decision and ask the room what they'd do."),
                discussion_points=[
                    "The before/after of the example.",
                    "The decision point that mattered.",
                ],
                link_to_reality="Use a scenario the audience will instantly recognise.",
                reflective_question="Where could you run this same play?",
                debrief="Seeing it once makes it yours to try.",
            ),
        ),
        exercise=ExerciseBlock(
            title=f"Exercise: apply {name}",
            fmt="pair",
            duration_min=12,
            steps=[
                "Pick a real task from your own work.",
                f"Apply {name} to it using the steps we just saw.",
                "Capture what changed and one thing you're unsure about.",
                "Swap with your partner and give one piece of feedback.",
            ],
            debrief_questions=[
                f"What was easy or hard about applying {name}?",
                "What will you keep doing differently?",
            ],
            notes=SpeakerNotes(
                aim=f"Let participants apply {name} to their own work.",
                time="12 min",
                instructions=("Put people in pairs. Give 8 minutes to work, 4 to "
                              "debrief. Circulate and unblock. Hold a 2-minute "
                              "plenary debrief at the end."),
                discussion_points=[
                    "Each pair applies it to a real task.",
                    "Surface a common sticking point.",
                    "Name one concrete improvement.",
                ],
                link_to_reality="Insist they use a real task, not a hypothetical.",
                reflective_question="What's the first task you'll use this on tomorrow?",
                debrief="You've now done it once — the second time is easier.",
            ),
        ),
    )


def _offline_subtopics(topic: str, n: int):
    base = [
        ("Foundations", "what it is and why it matters"),
        ("In practice", "seeing it work in a real context"),
        ("Applying it", "using it on your own work"),
        ("Going deeper", "patterns, pitfalls and judgment"),
        ("Scaling up", "making it stick beyond today"),
        ("Mastery", "edge cases and good habits"),
    ]
    out = []
    for i in range(n):
        name, hint = base[i % len(base)]
        out.append((f"{topic}: {name}", hint))
    return out


# --------------------------------------------------------------------------- #
# Defaults + healing
# --------------------------------------------------------------------------- #
def _default_title(tr: Training) -> str:
    return tr.topic[:1].upper() + tr.topic[1:] if tr.topic else "Training"


def _default_subtitle(tr: Training) -> str:
    return f"for {tr.audience.lower()} · {tr.level} level".strip(" ·")


def _as_list(v) -> List[str]:
    if v is None:
        return []
    if isinstance(v, str):
        return [v] if v.strip() else []
    return [str(x).strip() for x in v if str(x).strip()]


def _ensure_complete(tr: Training) -> None:
    """Heal any gaps so the deck builder always has valid content (edge cases)."""
    if not tr.title:
        tr.title = _default_title(tr)
    if not tr.subtitle:
        tr.subtitle = _default_subtitle(tr)
    if not tr.modules:
        _offline_plan(tr)
    if not tr.about.learning_objectives:
        tr.about.learning_objectives = [f"Understand {tr.topic}."]
    if not tr.about.learning_outcomes:
        tr.about.learning_outcomes = [f"Be able to {tr.objective.rstrip('.').lower()}."]
    if not tr.about.target_group:
        tr.about.target_group = f"{tr.audience} ({tr.level} level)."
    if not tr.agenda:
        tr.agenda = [m.name for m in tr.modules]
    if not tr.kickoff_goals:
        tr.kickoff_goals = [f"Set goals for {tr.topic}.", "Agree the agenda."]
    # ensure every block has non-empty notes
    for m in tr.modules:
        for blk in (m.theory, m.example, m.exercise):
            nt = blk.notes
            if not nt.aim:
                nt.aim = f"Cover {getattr(blk, 'title', m.name)}."
            if not nt.time:
                nt.time = "5 min"
            if not nt.instructions:
                nt.instructions = "Walk the slide, invite one comment, move on."
            if not nt.discussion_points:
                nt.discussion_points = ["The main point of this slide."]
            if not nt.link_to_reality:
                nt.link_to_reality = "Tie it to the audience's daily work."
            if not nt.reflective_question:
                nt.reflective_question = "How does this apply to you?"
            if not nt.debrief:
                nt.debrief = "Key point captured — let's continue."
    if not tr.wrapup.takeaways:
        tr.wrapup.takeaways = [f"You can now begin to {tr.objective.rstrip('.').lower()}."]
    if not tr.prebite.title:
        tr.prebite = Bite(title=f"Before we start: {tr.topic}", intro="", sections={})
    if not tr.postbite.title:
        tr.postbite = Bite(title=f"After the session: {tr.topic}", intro="", sections={})
