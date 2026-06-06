"""Turn a maverx `Training` into an ordered list of preview-slide dicts.

The order and content mirror `maverx/deck.py`'s `build_deck`, so the on-screen
carousel matches the generated PowerPoint slide-for-slide.
"""

from __future__ import annotations

from maverx.schema import Training


def build_preview_slides(tr: Training) -> list[dict]:
    slides: list[dict] = [
        {"kind": "cover", "title": tr.title or tr.topic, "subtitle": tr.subtitle},
    ]

    a = tr.about
    slides.append(
        {
            "kind": "about",
            "title": "About this session",
            "objectives": a.learning_objectives,
            "outcomes": a.learning_outcomes,
            "target_group": a.target_group,
            "good_to_know": a.good_to_know,
        }
    )

    if tr.trainer_timetable:
        slides.append(
            {
                "kind": "timetable",
                "title": "Timetable — trainer view",
                "rows": [
                    {"segment": r.segment, "minutes": r.minutes, "activity": r.activity}
                    for r in tr.trainer_timetable
                ],
            }
        )

    if tr.learner_timetable:
        slides.append(
            {
                "kind": "phases",
                "title": "What your day looks like",
                "phases": [p.split(" — ")[0] for p in tr.learner_timetable],
            }
        )

    if tr.agenda:
        slides.append({"kind": "agenda", "title": "Agenda", "items": tr.agenda})

    if tr.kickoff_goals:
        slides.append(
            {
                "kind": "kickoff",
                "title": "Kick-off: what you'll be able to do",
                "goals": tr.kickoff_goals,
            }
        )

    for i, m in enumerate(tr.modules, start=1):
        slides.append(
            {"kind": "section", "block": f"Module {i}", "title": f"{i}. {m.name}",
             "subtitle": "Theory  →  Example  →  Exercise"}
        )
        slides.append(
            {
                "kind": "theory", "block": "Theory", "title": m.theory.title or m.name,
                "definition": m.theory.definition, "points": m.theory.points,
                "statement": m.theory.statement,
            }
        )
        slides.append(
            {
                "kind": "example", "block": "Example",
                "title": m.example.title or f"{m.name} in practice",
                "scenario": m.example.scenario, "points": m.example.points,
            }
        )
        slides.append(
            {
                "kind": "exercise", "block": "Exercise",
                "title": m.exercise.title or f"Exercise: {m.name}",
                "fmt": m.exercise.fmt, "duration_min": m.exercise.duration_min,
                "steps": m.exercise.steps, "debrief": m.exercise.debrief_questions,
            }
        )

    slides.append({"kind": "section", "block": "Wrap-up", "title": "Wrap-up & reflection"})
    if tr.wrapup.takeaways:
        slides.append({"kind": "takeaways", "title": "Key takeaways", "items": tr.wrapup.takeaways})
    if tr.wrapup.whats_next:
        slides.append({"kind": "whats_next", "title": "What's next", "items": tr.wrapup.whats_next})
    slides.append(
        {
            "kind": "closing", "title": "To close it off",
            "reflection": tr.wrapup.reflection or ["What will you do differently after today?"],
        }
    )
    return slides
