"""FastAPI service for the Maverx Training Builder.

Drives the maverx pipeline (LLM planner + style-guided DeckBuilder) and adds a
web-friendly layer: a `/decks` orchestration endpoint that validates intake,
generates the styled deck + bites, persists history, and returns the Training
plan as preview slides; plus history and per-kind download routes.
"""

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from maverx.config import LLM
from maverx.intake import IntakeState
from maverx.llm import OpenRouterClient
from maverx.pipeline import generate_training
from maverx.planner import PlannerLLMError
from service import store
from service.preview import build_preview_slides

# How many AI follow-up (context-gathering) sub-questions per top-level question.
MAX_FOLLOWUPS = 2
_FOLLOWUP_KEYS = ("topic", "audience", "level", "duration", "objective")

PROJECT_ROOT = Path(__file__).resolve().parent
# Override with OUTPUT_DIR (env) to write/serve decks from a persistent disk (Render).
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", PROJECT_ROOT / "output")).resolve()

# kind -> (filename suffix, media type, optional .md fallback)
DOWNLOAD_KINDS = {
    "pptx": (".pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation"),
    "prebite": ("_pre-bite.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    "postbite": ("_post-bite.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    "plan": ("_plan.json", "application/json"),
}

app = FastAPI(title="Maverx Training Builder")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    store.init_db()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "llm": LLM.available(), "model": LLM.MODEL if LLM.available() else None}


def _duration_label(minutes: int) -> str:
    hours = (minutes or 0) / 60
    if hours <= 0:
        return "presentation"
    if abs(hours - round(hours)) < 0.05:
        whole = int(round(hours))
        return f"{whole} {'hour' if whole == 1 else 'hours'} presentation"
    if hours < 1:
        return f"{minutes} minutes presentation"
    return f"{hours:g} hours presentation"


def _heuristic_followup(key: str, answers: dict, thread: list) -> str | None:
    """Offline fallback: at most one clarifier for broad topic/objective answers."""
    if thread:
        return None
    val = str(answers.get(key, "")).strip()
    if key == "topic" and len(val.split()) <= 3:
        return f"Which specific aspect or use case of “{val}” should we focus on?"
    if key == "objective" and len(val.split()) <= 4:
        return "What does success look like in concrete terms for participants?"
    return None


def _llm_followup(client: OpenRouterClient, key: str, answers: dict, thread: list) -> str | None:
    """Ask the model whether more context is needed; return one follow-up or None."""
    labels = {
        "topic": "the training topic / skill", "audience": "the audience",
        "level": "the knowledge level", "duration": "the duration",
        "objective": "the learning objective",
    }
    context = "\n".join(f"- {k}: {v}" for k, v in answers.items() if v) or "- (nothing yet)"
    sub = "\n".join(f"  Q: {t.get('question')}\n  A: {t.get('answer')}" for t in thread)
    prompt = (
        "You are running the intake for a training-design assistant.\n"
        f"What the trainer has told us so far:\n{context}\n\n"
        f"You are deciding whether you have enough context about {labels.get(key, key)} "
        "to design a high-quality, specific training.\n"
        + (f"Follow-ups already asked & answered for this:\n{sub}\n\n" if sub else "")
        + "If you now have ENOUGH context, reply with exactly: OK\n"
        "Otherwise reply with ONE short, specific follow-up question (no preamble, no "
        "numbering, no quotes) that would most improve the result. Don't repeat anything asked."
    )
    try:
        out = client.complete(prompt, max_tokens=80, temperature=0.3).strip()
    except Exception:
        return None
    if not out or out.upper().startswith("OK") or len(out) < 5:
        return None
    return out.strip().strip('"').strip()


def _llm_extract(client: OpenRouterClient, message: str) -> dict:
    """Pull whichever of the 5 intake fields are clearly stated in the first
    message. Never invents — a field absent from the message stays empty."""
    prompt = (
        "A user described, in one message, a training they want built.\n"
        "Extract ONLY the fields that are clearly stated. If the message does "
        "not clearly state a field, leave it as an empty string. Never invent or "
        "infer beyond what is written.\n\n"
        f"MESSAGE:\n{message}\n\n"
        "Return a single JSON object with EXACTLY these string keys:\n"
        '{"topic":"","audience":"","level":"","duration":"","objective":""}\n'
        "- topic: the subject or skill to be trained\n"
        "- audience: who the training is for\n"
        "- level: only if stated (beginner / intermediate / advanced)\n"
        "- duration: only if stated (e.g. '2 hours', 'half a day')\n"
        "- objective: the goal — what participants should be able to do after\n"
    )
    try:
        data = client.complete_json(prompt, temperature=0.1, max_tokens=400)
    except Exception:
        return _heuristic_extract(message)
    out = {}
    for k in _FOLLOWUP_KEYS:
        v = str((data or {}).get(k, "")).strip()
        if v:
            out[k] = v
    return out


def _heuristic_extract(message: str) -> dict:
    """Offline fallback: light, conservative parsing. Detects level/duration by
    keyword, and uses a short message verbatim as the topic. No guessing."""
    import re

    out: dict = {}
    low = message.lower()
    for lvl in ("beginner", "intermediate", "advanced", "novice", "expert"):
        if lvl in low:
            out["level"] = "beginner" if lvl == "novice" else (
                "advanced" if lvl == "expert" else lvl)
            break
    m = re.search(r"(half|full)\s+(a\s+)?day|\d+(?:[.,]\d+)?\s*(hours?|hrs?|h|minutes?|mins?|days?)", low)
    if m:
        out["duration"] = m.group(0).strip()
    # A short opening line is almost always just the topic.
    if len(message.split()) <= 8:
        out["topic"] = message.strip()
    return out


@app.post("/intake/extract")
def intake_extract(body: dict) -> dict:
    """Pre-fill: extract any intake answers already present in the user's first
    message, so the matching questions arrive pre-filled (and editable)."""
    message = str(body.get("message", "")).strip()
    if not message:
        return {"fields": {}}
    client = OpenRouterClient()
    fields = (
        _llm_extract(client, message)
        if client.available
        else _heuristic_extract(message)
    )
    return {"fields": fields}


@app.post("/intake/followup")
def intake_followup(body: dict) -> dict:
    """Return the next context-gathering follow-up for a question, or null when
    the AI has enough context (or the per-question cap is reached)."""
    key = str(body.get("key", "")).strip()
    answers = body.get("answers", {}) or {}
    thread = body.get("thread", []) or []
    if key not in _FOLLOWUP_KEYS or len(thread) >= MAX_FOLLOWUPS:
        return {"followup": None}
    client = OpenRouterClient()
    followup = (
        _llm_followup(client, key, answers, thread)
        if client.available
        else _heuristic_followup(key, answers, thread)
    )
    return {"followup": followup}


@app.post("/decks")
def create_deck(answers: dict) -> dict:
    """Validate intake, run the maverx pipeline, persist, return preview slides."""
    fields = {
        "topic": str(answers.get("topic", "")).strip(),
        "audience": str(answers.get("audience", "")).strip(),
        "level": str(answers.get("level") or answers.get("knowledge_level") or "").strip(),
        "duration": str(answers.get("duration", "")).strip(),
        "objective": str(answers.get("objective") or answers.get("primary_objective") or "").strip(),
    }

    state = IntakeState()
    errors: dict[str, str] = {}
    for key in ("topic", "audience", "level", "duration", "objective"):
        ok, followup = state.record(key, fields[key])
        if not ok:
            errors[key] = followup or "Please refine this answer."
    if errors:
        raise HTTPException(
            status_code=422,
            detail={"issues": [f"{k}: {v}" for k, v in errors.items()], "followups": errors},
        )

    deck_id = uuid.uuid4().hex[:12]
    deck_dir = (OUTPUT_DIR / deck_id).resolve()
    # When a key is configured, the LLM is the expected engine: surface a failure
    # rather than silently shipping the generic offline template as a real deck.
    llm_available = LLM.available()
    try:
        result = generate_training(
            state.answers,
            out_dir=deck_dir,
            use_llm=llm_available,
            require_llm=llm_available,
        )
    except PlannerLLMError as e:
        raise HTTPException(
            status_code=502,
            detail={
                "error": "ai_generation_failed",
                "message": "The AI model failed to generate this training. "
                           "Please try again.",
                "detail": str(e),
            },
        )
    tr = result.training

    slides = build_preview_slides(tr)
    downloads = {kind: f"/decks/{deck_id}/download/{kind}" for kind in DOWNLOAD_KINDS}
    payload = {
        "deck_id": deck_id,
        "slug": result.slug,
        "title": tr.title or tr.topic or "Untitled training",
        "subtitle": tr.subtitle,
        "model_name": result.generated_by,
        "ai_generated": result.used_llm,
        "engine": "llm" if result.used_llm else "offline",
        "module_count": len(tr.modules),
        "page_count": len(slides),
        "duration_label": _duration_label(tr.duration_min),
        "slides": slides,
        "downloads": downloads,
        "download_url": downloads["pptx"],
    }

    store.save_deck(
        {
            "id": deck_id,
            "title": payload["title"],
            "tier": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "page_count": payload["page_count"],
            "duration_label": payload["duration_label"],
            "model_name": result.generated_by,
            "slug": result.slug,
            "payload": payload,
        }
    )
    return payload


@app.get("/decks")
def list_decks() -> dict:
    return {"groups": store.list_grouped()}


@app.get("/decks/{deck_id}")
def get_deck(deck_id: str) -> dict:
    record = store.get_deck(deck_id)
    if not record:
        raise HTTPException(status_code=404, detail="Deck not found.")
    return record["payload"]


@app.get("/decks/{deck_id}/download/{kind}")
def download_deck(deck_id: str, kind: str) -> FileResponse:
    if kind not in DOWNLOAD_KINDS:
        raise HTTPException(status_code=400, detail=f"Unknown kind '{kind}'.")
    record = store.get_deck(deck_id)
    if not record or not record.get("slug"):
        raise HTTPException(status_code=404, detail="Deck not found.")
    slug = record["slug"]
    suffix, media = DOWNLOAD_KINDS[kind]
    deck_dir = (OUTPUT_DIR / deck_id).resolve()

    candidates = [deck_dir / f"{slug}{suffix}"]
    if kind in ("prebite", "postbite"):  # .md fallback when python-docx is absent
        candidates.append(deck_dir / f"{slug}{suffix.replace('.docx', '.md')}")
    for path in candidates:
        if path.is_file() and path.resolve().parent == deck_dir:
            return FileResponse(str(path), media_type=media, filename=path.name)
    raise HTTPException(status_code=404, detail=f"No '{kind}' file for this deck.")
