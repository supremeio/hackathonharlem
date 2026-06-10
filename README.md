# Maverx AI Training Builder

Turn a one-line brief into a complete, on-brand training program: an editable
PowerPoint deck in the Maverx house style, with trainer speaker notes on every
slide, plus pre- and post-session companion documents.

A conversational web app sits on top of a Python pipeline: describe a training,
answer a few AI follow-up questions, watch it generate, preview the styled slides,
and download the deck.

## Architecture

A monorepo with two runtimes:

```
frontend/          Next.js 14 (App Router) + Tailwind — the conversational UI
  app/demo/        an auto-playing, self-contained product showcase (no backend)
api.py             FastAPI service — intake validation, orchestration, downloads
maverx/            the generation engine (LLM planner → typed Training → DeckBuilder)
  planner.py       brief → typed Training (LLM, with a deterministic offline fallback)
  deck.py          renders the editable .pptx on the Maverx master template
  bites.py         pre/post-bite .docx
  config.py        house style (palette, Space Grotesk) + LLM config
service/           store.py (SQLite history) + preview.py (Training → preview slides)
tests/             offline pipeline smoke tests (no network/key required)
```

The frontend is a pure client of the backend (`${NEXT_PUBLIC_API_BASE}/decks`), so
the two deploy independently.

## Run locally

Prerequisites: Python 3.10+ and Node.js 18+.

**Backend** (FastAPI) — from the repo root:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # add your OPENROUTER_API_KEY
uvicorn api:app --reload --port 8000
curl -s http://localhost:8000/health   # expect {"status":"ok","llm":true,...}
```

**Frontend** (Next.js) — in a second terminal:

```bash
cd frontend
npm install
cp .env.example .env.local    # NEXT_PUBLIC_API_BASE=http://localhost:8000
npm run dev                   # open the URL it prints (e.g. http://localhost:3000)
```

Without an API key the app still runs: it falls back to the deterministic offline
planner and clearly labels the result "Generated offline · AI off".

## How generation works

`maverx/` builds a typed `Training` from the brief, then renders it:

1. **Plan** (`planner.py`) — an LLM (OpenRouter / Claude Sonnet 4.6) produces a
   training following a fixed didactic arc (Kick-off → Theory → Example → Exercise
   → Wrap-up) with speaker notes on every slide. If no key is configured, a
   deterministic offline planner produces a valid training instead.
2. **Render** (`deck.py`, `bites.py`) — the plan is injected into the Maverx master
   `.pptx` (fonts, colours, logo preserved, fully editable) plus pre/post-bite docs.
3. **Preview** (`service/preview.py`) — the same plan is returned as ordered preview
   slides, so the on-screen preview matches the downloadable deck exactly.

If the LLM is expected but fails, `/decks` returns `502` rather than silently
shipping a generic offline deck.

## Environment variables

Secrets are never committed — `.env` and `frontend/.env.local` are gitignored.

| Variable | Where | Required | Purpose |
|---|---|---|---|
| `OPENROUTER_API_KEY` | backend `.env` | for AI generation | OpenRouter key (`sk-or-…`). |
| `OPENROUTER_MODEL` | backend `.env` | no | Model id; defaults to `anthropic/claude-sonnet-4.6`. |
| `OPENROUTER_TEMPERATURE` / `OPENROUTER_MAX_TOKENS` | backend `.env` | no | Generation tuning. |
| `NEXT_PUBLIC_API_BASE` | frontend `.env.local` | yes | URL of the backend. |
| `OUTPUT_DIR` / `DECKS_DB` | backend (deploy) | no | Point generated files + history at a persistent disk. |

Manage keys at <https://openrouter.ai/keys>.

## Web API

- `POST /decks` — validate intake, run the pipeline, persist, return preview slides
  + download links. `422` (with issues) for vague intake; `502` on AI failure.
- `GET /decks` — history grouped Today / Yesterday / Earlier.
- `GET /decks/{id}` — a previously generated deck (preview slides).
- `GET /decks/{id}/download/{kind}` — `kind ∈ pptx | prebite | postbite | plan`.
- `POST /intake/extract` — pull any of the 5 fields already present in the first message.
- `POST /intake/followup` — the next AI clarifying question, or none.
- `GET /health` — status + whether the LLM is configured.

CORS is open for local/demo use; restrict `allow_origins` before production.

## Deployment

**Frontend → Vercel:** import the repo, set **Root Directory = `frontend`**, add
`NEXT_PUBLIC_API_BASE` pointing at the backend URL.

**Backend → Render** (`render.yaml` blueprint) **or Railway** (`Procfile`). Set
`OPENROUTER_API_KEY` in the dashboard; mount a disk and set `OUTPUT_DIR` / `DECKS_DB`
to it for persistent history and downloads.

## Tests

```bash
python -m unittest discover -s tests   # offline pipeline smoke tests
```
