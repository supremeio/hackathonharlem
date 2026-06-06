"""Generate pre-bites, post-bites, and dataset specifications."""

from generation.fallback import LEVEL_NAMES, _localized


def generate_artifacts(intake: dict, level: int) -> tuple[dict, dict, dict]:
    topic = intake["topic"]
    audience = intake["audience"]
    level_name = LEVEL_NAMES[level]
    next_focus = "real-world application" if level == 3 else f"Level {level + 1} preparation"

    prebite = {
        "title": _localized(intake, f"Prepare for {topic}: {level_name}", f"Voorbereiding op {topic}: {level_name}"),
        "output_language": intake["output_language"],
        "estimated_minutes": 15,
        "purpose": _localized(intake, f"Activate the knowledge needed for Level {level}.", f"Activeer de kennis die nodig is voor Level {level}."),
        "content": [
            _localized(intake, f"Review a recent {topic} task from your work.", f"Bekijk een recente {topic}-taak uit je werk."),
            _localized(intake, f"Note one success and one challenge relevant to {audience}.", f"Noteer één succes en één uitdaging voor {audience}."),
        ],
        "reflection_questions": [
            _localized(intake, f"What would a strong {topic} result look like?", f"Hoe ziet een sterk {topic}-resultaat eruit?"),
            _localized(intake, "Which decision currently feels hardest?", "Welke beslissing voelt nu het moeilijkst?"),
        ],
    }
    postbite = {
        "title": _localized(intake, f"Continue applying {topic}: {level_name}", f"Blijf {topic} toepassen: {level_name}"),
        "output_language": intake["output_language"],
        "estimated_minutes": 20,
        "summary": _localized(intake, f"Turn Level {level} learning into a repeatable workplace habit.", f"Maak van Level {level}-leren een herhaalbare werkgewoonte."),
        "reflection_questions": [
            _localized(intake, "What changed in your approach?", "Wat veranderde er in je aanpak?"),
            _localized(intake, "What evidence shows that the result improved?", "Welk bewijs laat zien dat het resultaat verbeterde?"),
        ],
        "assignment": _localized(intake, f"Apply one Level {level} technique to a real task and record the outcome.", f"Pas één Level {level}-techniek toe op een echte taak en leg het resultaat vast."),
        "next_level_bridge": _localized(intake, f"Use the result as input for {next_focus}.", f"Gebruik het resultaat als input voor {next_focus}."),
    }
    dataset = _dataset(intake, level)
    return prebite, postbite, dataset


def _dataset(intake: dict, level: int) -> dict:
    topic = intake["topic"]
    audience = intake["audience"]
    columns = [
        {"name": "item_id", "type": "integer", "description": "Unique practice item", "adjustable": False},
        {"name": "category", "type": "string", "description": f"Category relevant to {topic}", "adjustable": True},
        {"name": "value", "type": "number", "description": "Primary value for analysis", "adjustable": True},
    ]
    if level >= 2:
        columns.extend([
            {"name": "target", "type": "number", "description": "Comparison target", "adjustable": True},
            {"name": "variance", "type": "calculated number", "description": "Value minus target", "adjustable": False},
        ])
    if level == 3:
        columns.extend([
            {"name": "risk_signal", "type": "string", "description": "Signal requiring interpretation", "adjustable": True},
            {"name": "recommended_action", "type": "string", "description": "Decision based on evidence", "adjustable": True},
        ])
    complexity = {1: "simple guided analysis", 2: "multi-column analysis with calculated fields", 3: "complex interpretation and decision-making"}[level]
    return {
        "title": _localized(intake, f"{topic} Level {level} practice dataset", f"{topic} Level {level} oefendataset"),
        "scenario": _localized(intake, f"{audience} use a {complexity} dataset.", f"{audience} gebruiken een dataset voor {complexity}."),
        "level": level,
        "columns": columns,
        "sample_rows": [],
        "expected_outcome": _localized(intake, f"Participants produce and justify a Level {level} result.", f"Deelnemers maken en onderbouwen een Level {level}-resultaat."),
    }
