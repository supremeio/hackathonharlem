"""Content generation: deterministic skeleton, optionally enriched by an LLM.

The deterministic fallback guarantees a schema-valid deck (exactly 20 slides,
correct block order, allowed slide types, full speaker notes, level progression).
When OPENROUTER_API_KEY is set we ask the model to rewrite only the *text* of
each slide for the specific topic/audience, keep the structure intact, then
re-validate. Any failure silently keeps the deterministic content, so the
pipeline always produces a valid result.
"""

import json
import os
from typing import Optional

from generation.artifacts import generate_artifacts
from generation.cost import estimate_tokens
from generation.fallback import generate_deck
from generation.validator import validate_artifacts, validate_deck, ensure_valid

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Text fields the LLM is allowed to rewrite; structure stays deterministic.
_EDITABLE = ("title", "body", "visual_suggestion", "confidence_reason")
_NOTE_FIELDS = (
    "aim",
    "time",
    "instructions",
    "reflective_question",
    "debrief",
    "key_discussion_points",
    "link_to_reality",
)


def generate_outputs(intake: dict) -> tuple[dict[str, dict], str, bool]:
    """Return (outputs, model_name, used_llm).

    `outputs` maps filename -> deck/artifact dict, exactly like generate_all,
    but decks may be LLM-enriched. Always schema-valid.
    """
    levels = [1] if intake.get("tier") == 1 else [1, 2, 3]
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    model_name = os.environ.get("MODEL_NAME", "").strip()
    can_use_llm = bool(api_key and model_name)

    outputs: dict[str, dict] = {}
    used_llm = False
    for level in levels:
        deck = generate_deck(intake, level)
        if can_use_llm:
            enriched = _try_enrich(deck, intake, level, api_key, model_name)
            if enriched is not None:
                deck = enriched
                used_llm = True
        prebite, postbite, dataset = generate_artifacts(intake, level)
        ensure_valid(validate_deck(deck, intake, level))
        ensure_valid(validate_artifacts(prebite, postbite, dataset, intake, level))
        outputs[f"slides_L{level}.json"] = deck
        outputs[f"prebite_L{level}.json"] = prebite
        outputs[f"postbite_L{level}.json"] = postbite
        outputs[f"dataset_spec_L{level}.json"] = dataset

    return outputs, (model_name if used_llm else "deterministic-fallback"), used_llm


def _try_enrich(
    deck: dict, intake: dict, level: int, api_key: str, model_name: str
) -> Optional[dict]:
    """Ask the LLM to rewrite slide text; return an enriched deck or None."""
    try:
        import requests

        skeleton = [
            {
                "slide_number": s["slide_number"],
                "slide_type": s["slide_type"],
                "block": s["block"],
                "title": s["title"],
                "body": s["body"],
            }
            for s in deck["slides"]
        ]
        prompt = _build_prompt(intake, level, skeleton)
        response = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model_name,
                "messages": [
                    {"role": "system", "content": _SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.4,
                "response_format": {"type": "json_object"},
            },
            timeout=90,
        )
        response.raise_for_status()
        payload = response.json()
        content = payload["choices"][0]["message"]["content"]
        data = json.loads(content)
        new_slides = data.get("slides", data if isinstance(data, list) else [])

        merged = _merge(deck, new_slides, intake)
        if validate_deck(merged, intake, level):
            return None  # enriched deck failed validation → keep deterministic

        usage = payload.get("usage", {}) or {}
        merged["generation_mode"] = "llm_enriched"
        merged["model_name"] = model_name
        merged["cost_tracking"] = {
            "model_name": model_name,
            "input_tokens_estimate": usage.get("prompt_tokens")
            or estimate_tokens(prompt),
            "output_tokens_estimate": usage.get("completion_tokens")
            or estimate_tokens(content),
            "estimated_cost_eur": None,
        }
        return merged
    except Exception:
        return None


def _merge(deck: dict, new_slides: list, intake: dict) -> dict:
    """Overlay LLM text onto the deterministic deck, keeping structure."""
    by_number = {s.get("slide_number"): s for s in new_slides if isinstance(s, dict)}
    merged = json.loads(json.dumps(deck))  # deep copy
    for slide in merged["slides"]:
        incoming = by_number.get(slide["slide_number"])
        if not incoming:
            continue
        if isinstance(incoming.get("title"), str) and incoming["title"].strip():
            slide["title"] = incoming["title"].strip()
        if isinstance(incoming.get("body"), list) and incoming["body"]:
            slide["body"] = [str(item) for item in incoming["body"] if str(item).strip()]
        if isinstance(incoming.get("visual_suggestion"), str) and incoming["visual_suggestion"].strip():
            slide["visual_suggestion"] = incoming["visual_suggestion"].strip()
        if isinstance(incoming.get("confidence_reason"), str) and incoming["confidence_reason"].strip():
            slide["confidence_reason"] = incoming["confidence_reason"].strip()
        score = incoming.get("confidence_score")
        if isinstance(score, (int, float)) and not isinstance(score, bool):
            slide["confidence_score"] = max(0.0, min(1.0, float(score)))
        notes = incoming.get("speaker_notes")
        if isinstance(notes, dict):
            for field in _NOTE_FIELDS:
                value = notes.get(field)
                if field == "key_discussion_points":
                    if isinstance(value, list) and value:
                        slide["speaker_notes"][field] = [str(v) for v in value if str(v).strip()]
                elif isinstance(value, str) and value.strip():
                    slide["speaker_notes"][field] = value.strip()
    return merged


_SYSTEM = (
    "You are an expert instructional designer producing corporate training slides. "
    "You rewrite slide text to be specific, practical, and engaging while strictly "
    "preserving the provided structure. You always return valid JSON."
)


def _build_prompt(intake: dict, level: int, skeleton: list) -> str:
    lang = {
        "en": "English",
        "nl": "Dutch",
        "bilingual": "bilingual — each string formatted exactly as 'NL: <dutch>\\nEN: <english>'",
    }[intake["output_language"]]
    return (
        f"Training topic: {intake['topic']}\n"
        f"Audience: {intake['audience']} (knowledge level: {intake['knowledge_level']})\n"
        f"Primary objective: {intake['primary_objective']}\n"
        f"Module level: {level}\n"
        f"Output language: {lang}\n\n"
        "Below is a slide skeleton. Rewrite the TEXT to be specific and useful for "
        "this exact topic and audience. Keep slide_number, slide_type and block "
        "unchanged. Keep 'body' as an array of 2-5 short strings.\n\n"
        "Return a JSON object: {\"slides\": [ ... ]}. Each slide object must include: "
        "slide_number, title, body (array of strings), visual_suggestion, "
        "confidence_score (0-1), confidence_reason, and speaker_notes with fields "
        "aim, time, instructions, reflective_question, debrief, "
        "key_discussion_points (array of strings), link_to_reality.\n\n"
        f"Skeleton:\n{json.dumps(skeleton, ensure_ascii=False)}"
    )
