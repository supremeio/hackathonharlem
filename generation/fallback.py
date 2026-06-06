"""Deterministic, audience-aware slide generation."""

from generation.cost import MODEL_NAME, build_cost_tracking

BLOCK_ORDER = ["kick-off", "theory", "example", "exercise", "wrap-up"]
LEVEL_NAMES = {1: "Essentials", 2: "Advanced", 3: "Expert"}
ALLOCATIONS = {
    1: {"kick-off": 3, "theory": 5, "example": 4, "exercise": 5, "wrap-up": 3},
    2: {"kick-off": 4, "theory": 5, "example": 4, "exercise": 4, "wrap-up": 3},
    3: {"kick-off": 4, "theory": 5, "example": 4, "exercise": 4, "wrap-up": 3},
}


def generate_deck(intake: dict, level: int) -> dict:
    slides = []
    for block in BLOCK_ORDER:
        for index in range(ALLOCATIONS[level][block]):
            slides.append(_build_slide(intake, level, block, index))
    for number, slide in enumerate(slides, start=1):
        slide["slide_number"] = number

    deck = {
        "schema_version": "1.0",
        "generation_mode": "deterministic_fallback",
        "output_language": intake["output_language"],
        "model_name": MODEL_NAME,
        "cost_tracking": {},
        "slides": slides,
    }
    deck["cost_tracking"] = build_cost_tracking(intake, deck)
    return deck


def _build_slide(intake: dict, level: int, block: str, index: int) -> dict:
    topic = intake["topic"]
    audience = intake["audience"]
    level_name = LEVEL_NAMES[level]
    slide_type, title_en, title_nl, body_en, body_nl = _content(
        intake, level, block, index
    )
    structural = slide_type.startswith("kickoff_") or slide_type.startswith("wrapup_")
    score = 0.75 if structural else 0.50 if intake["outline_path"] == "research_assisted" else 0.65
    reason_en = (
        "Structural slide based on the fixed Maverx didactic model."
        if structural
        else "Generated from deterministic teaching templates without external research."
    )
    reason_nl = (
        "Structuurslide gebaseerd op het vaste didactische Maverx-model."
        if structural
        else "Gegenereerd met deterministische onderwijssjablonen zonder extern onderzoek."
    )
    focus = title_en
    return {
        "slide_number": 0,
        "slide_type": slide_type,
        "block": block,
        "level": level,
        "title": _localized(intake, title_en, title_nl),
        "body": [_localized(intake, en, nl) for en, nl in zip(body_en, body_nl)],
        "table": None,
        "visual_suggestion": _localized(
            intake,
            f"Use a clean Maverx layout with one visual metaphor for {focus}.",
            f"Gebruik een heldere Maverx-layout met één visuele metafoor voor {focus}.",
        ),
        "confidence_score": score,
        "confidence_reason": _localized(intake, reason_en, reason_nl),
        "speaker_notes": _notes(intake, level_name, block, focus, topic, audience),
    }


def _content(intake: dict, level: int, block: str, index: int) -> tuple:
    topic = intake["topic"]
    audience = intake["audience"]
    objective = intake["primary_objective"]
    level_name = LEVEL_NAMES[level]
    prior = intake.get("presupposes") or [f"{topic} foundations", "core workflow", "basic practice"]
    prior_text = ", ".join(prior[:3])

    if block == "kick-off":
        types = ["kickoff_title", "kickoff_agenda", "kickoff_objectives"]
        if level > 1:
            types.append("mentimeter_recap")
        slide_type = types[index]
        if slide_type == "kickoff_title":
            return slide_type, f"{topic}: {level_name}", f"{topic}: {level_name}", [
                f"A practical Level {level} session for {audience}.",
                f"Focus: {objective}",
            ], [
                f"Een praktische Level {level}-sessie voor {audience}.",
                f"Focus: {objective}",
            ]
        if slide_type == "kickoff_agenda":
            arc = " → ".join(BLOCK_ORDER)
            return slide_type, "Today’s learning journey", "De leerroute van vandaag", [
                arc,
                "Expect short explanations, practical examples, and active application.",
            ], [
                arc,
                "Verwacht korte uitleg, praktische voorbeelden en actieve toepassing.",
            ]
        if slide_type == "kickoff_objectives":
            return slide_type, "Learning objectives", "Leerdoelen", [
                objective,
                f"Apply {topic} in the daily context of {audience}.",
                "Explain choices and evaluate the result.",
            ], [
                objective,
                f"Pas {topic} toe in de dagelijkse context van {audience}.",
                "Leg keuzes uit en beoordeel het resultaat.",
            ]
        questions = [
            f"1. What is the purpose of {prior[0]}?",
            f"2. When would you use {prior[1]}?",
            f"3. What common mistake affects {prior[2]}?",
            f"4. How do the Level {level - 1} concepts connect?",
            f"5. What would you improve in a previous example?",
        ]
        return slide_type, f"Mentimeter recap: Level {level - 1}", f"Mentimeter-terugblik: Level {level - 1}", questions, [
            f"1. Wat is het doel van {prior[0]}?",
            f"2. Wanneer gebruik je {prior[1]}?",
            f"3. Welke veelgemaakte fout beïnvloedt {prior[2]}?",
            f"4. Hoe hangen de concepten van Level {level - 1} samen?",
            "5. Wat zou je verbeteren aan een eerder voorbeeld?",
        ]

    if block == "theory":
        slide_type = "theory_intro" if index == 0 else "theory_deep"
        concept = [
            "the core workflow",
            "quality criteria",
            "decision points",
            "common failure patterns",
            "a repeatable improvement cycle",
        ][index]
        progression = _progression(level, prior_text)
        return slide_type, f"Concept {index + 1}: {concept}", f"Concept {index + 1}: {concept}", [
            f"Define {concept} for {topic}.",
            f"Connect it to the work of {audience}.",
            progression,
        ], [
            f"Definieer {concept} voor {topic}.",
            f"Verbind het met het werk van {audience}.",
            progression,
        ]

    if block == "example":
        slide_type = "example_walkthrough" if index % 2 == 0 else "example_case"
        scenario = f"a {audience} team handling a realistic {topic} task"
        return slide_type, f"Example {index + 1}: from need to result", f"Voorbeeld {index + 1}: van behoefte naar resultaat", [
            f"Scenario: {scenario}.",
            f"Step {index + 1}: choose an approach and make the reasoning visible.",
            f"Check the result against the Level {level} quality criteria.",
        ], [
            f"Scenario: {scenario}.",
            f"Stap {index + 1}: kies een aanpak en maak de redenering zichtbaar.",
            f"Toets het resultaat aan de kwaliteitscriteria van Level {level}.",
        ]

    if block == "exercise":
        slide_type = "exercise_setup" if index == 0 else "exercise_instructions"
        difficulty = {
            1: "Follow the provided steps and explain one choice.",
            2: "Compare two approaches, adapt the workflow, and justify your choice.",
            3: "Synthesize competing signals, make a judgment, and defend the trade-offs.",
        }[level]
        return slide_type, f"Exercise {index + 1}: apply {topic}", f"Oefening {index + 1}: pas {topic} toe", [
            f"1. Review the scenario for {audience}.",
            f"2. {difficulty}",
            "3. Prepare a two-minute explanation of the result.",
        ], [
            f"1. Bekijk het scenario voor {audience}.",
            f"2. {difficulty}",
            "3. Bereid een uitleg van twee minuten over het resultaat voor.",
        ]

    slide_types = ["wrapup_summary", "wrapup_nextlevel", "wrapup_summary"]
    slide_type = slide_types[index]
    if index == 0:
        body_en = ["Name the three ideas that matter most.", "Connect each idea to tomorrow’s work.", "Identify one remaining question."]
        body_nl = ["Noem de drie belangrijkste ideeën.", "Verbind elk idee met het werk van morgen.", "Benoem één openstaande vraag."]
        title_en, title_nl = "Key takeaways", "Belangrijkste inzichten"
    elif index == 1:
        next_step = "real-world application" if level == 3 else f"Level {level + 1}"
        body_en = [f"Use this session as the bridge to {next_step}.", "Choose one practice action for the next week."]
        body_nl = [f"Gebruik deze sessie als brug naar {next_step}.", "Kies één oefenactie voor de komende week."]
        title_en, title_nl = "Next step", "Volgende stap"
    else:
        body_en = [objective, "Share one commitment with the group.", "Close with the practical value for the audience."]
        body_nl = [objective, "Deel één toezegging met de groep.", "Sluit af met de praktische waarde voor de doelgroep."]
        title_en, title_nl = "Commit to practice", "Maak de stap naar de praktijk"
    return slide_type, title_en, title_nl, body_en, body_nl


def _progression(level: int, prior_text: str) -> str:
    if level == 1:
        return "Build a beginner-friendly foundation before adding complexity."
    if level == 2:
        return f"Build explicitly on Level 1 concepts: {prior_text}."
    return f"Synthesize Level 1 foundations and Level 2 advanced practice: {prior_text}."


def _notes(intake: dict, level_name: str, block: str, focus: str, topic: str, audience: str) -> dict:
    pairs = {
        "aim": (f"Help participants understand and use {focus}.", f"Help deelnemers {focus} begrijpen en gebruiken."),
        "time": ("5 min", "5 min"),
        "instructions": (
            f"Introduce the purpose, invite one response, explain the key point, and connect it to {topic}.",
            f"Introduceer het doel, vraag één reactie, leg het kernpunt uit en verbind dit met {topic}.",
        ),
        "reflective_question": (
            f"Where does this show up in the daily work of {audience}?",
            f"Waar komt dit terug in het dagelijkse werk van {audience}?",
        ),
        "debrief": (
            f"Close by naming the practical Level {level_name} insight participants should retain.",
            f"Sluit af met het praktische Level {level_name}-inzicht dat deelnemers moeten onthouden.",
        ),
        "link_to_reality": (
            f"Relate the discussion to a realistic decision faced by {audience}.",
            f"Verbind de discussie met een realistische beslissing van {audience}.",
        ),
    }
    notes = {key: _localized(intake, en, nl) for key, (en, nl) in pairs.items()}
    notes["key_discussion_points"] = [
        _localized(intake, f"Why {focus} matters.", f"Waarom {focus} belangrijk is."),
        _localized(intake, f"How it supports {topic}.", f"Hoe dit {topic} ondersteunt."),
        _localized(intake, "What good practice looks like.", "Hoe goede toepassing eruitziet."),
    ]
    return notes


def _localized(intake: dict, en: str, nl: str) -> str:
    language = intake["output_language"]
    if language == "nl":
        return nl
    if language == "bilingual":
        return f"NL: {nl}\nEN: {en}"
    return en
