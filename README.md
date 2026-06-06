# Maverx AI Training Builder

Person A is the front door and pipeline wiring for the Maverx AI Training Builder. Person B turns the validated intake into deterministic, structured training content that Person C can render.

## Web Application (full product)

This repo is now a monorepo: the Python pipeline lives at the root and a Next.js
web client lives in [`frontend/`](frontend/). The web app drives the whole flow —
conversational intake → validation → generation → `.pptx` rendering → preview &
download — for **Tier 1** (one deck).

> The web demo currently generates a single training deck. Multi-level Tier 2 JSON generation is available in the CLI fallback pipeline.

### Run it locally

Prerequisites: Python 3.10+ and Node.js 18+.

Backend (FastAPI) — from the repo root:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn api:app --reload --port 8000
```

Frontend (Next.js) — in a second terminal:

```bash
cd frontend
npm install
cp .env.example .env.local   # NEXT_PUBLIC_API_BASE=http://localhost:8000
npm run dev                  # http://localhost:3001
```

### Generation engine

The deck is produced by the **maverx pipeline** (`maverx/`): an LLM planner builds
a typed `Training`, then the style-guided `DeckBuilder` (`maverx/deck.py` +
`maverx/config.py` house style) renders an editable `.pptx` on the Maverx master,
plus pre/post-bite `.docx`. The on-screen preview renders the same `Training`
plan with the brand palette + Space Grotesk/Raleway, so preview and deck match.

By default it uses the **offline planner** (no API key). To enable the LLM, set in `.env`:

```bash
OPENROUTER_API_KEY=<your-openrouter-key>
OPENROUTER_MODEL=anthropic/claude-sonnet-4.6   # any OpenRouter model id
```

It falls back to the offline planner automatically when no key is present.

### Web API

In addition to the prototype routes, the client uses:

- `POST /decks` — accepts the client's answers, validates intake (422 with
  `{issues, followups}` if vague/incomplete), runs the maverx pipeline, persists,
  and returns the `Training` plan as ordered preview slides + download URLs.
- `GET /decks` — deck history grouped Today / Yesterday / Earlier.
- `GET /decks/{id}` — a previously generated deck (its preview slides).
- `GET /decks/{id}/download/{kind}` — `kind` ∈ `pptx | prebite | postbite | plan`.

CORS is enabled and history is persisted to SQLite under `data/` (gitignored).

---

The sections below document the original Person A / B / C pipeline contracts.

## Person A Responsibilities

- Conversational intake with field-specific follow-ups
- Natural-language duration parsing
- Validation gate and Training Readiness Score
- Resume support through `intake_draft.json`
- Shared intake and slide JSON schemas
- Orchestration stubs for Person B and Person C
- Friendly errors and a dry-run demo flow
- Outline-path and output-language contracts for future generation

## Quickstart

Requires Python 3.10 or newer. The web frontend requires Node.js 18+.

```bash
git clone https://github.com/isaackim1/hackathonhaarlem.git
cd hackathonhaarlem
python main.py
```

Useful modes:

```bash
python main.py --dry-run
python main.py --resume
python main.py --output path/to/intake.json
python main.py --debug
```

Copy `.env.example` to `.env` when Person B adds API-backed generation. Person A does not read or require these variables.

## Intake Flow

The CLI asks, in order:

1. Challenge tier
2. Topic or skill
3. Target audience
4. Participant knowledge level
5. Duration
6. Primary learning objective
7. Outline creation path
8. Output language
9. Module level
10. Previous concepts, only for Level 2 or 3

Each field gets at most three attempts. After three invalid attempts, partial answers are saved to `intake_draft.json`. `python main.py --resume` loads the draft and skips answers that are already valid.

## Intake Schema

The full machine-readable contract is in `schemas/intake_schema.json`. A successful intake includes:

```json
{
  "tier": 2,
  "topic": "Power BI dashboard design for campaign reporting",
  "audience": "junior marketing analysts who report campaign performance",
  "knowledge_level": "intermediate",
  "duration_hours": 3.0,
  "primary_objective": "By the end of this session, participants will be able to build and explain a campaign dashboard.",
  "outline_path": "research_assisted",
  "output_language": "bilingual",
  "level": 2,
  "presupposes": ["data import", "basic charts", "filters"],
  "slide_target": 36,
  "didactic_blocks": ["kick-off", "theory", "example", "exercise", "wrap-up"],
  "speaker_notes_fields": ["aim", "time", "instructions", "reflective_question", "debrief"],
  "prebite_required": true,
  "postbite_required": true,
  "cost_tracking_required": true,
  "slide_confidence_required": true,
  "iterative_confirmation_required": true
}
```

### Outline Path

`outline_path` records how Person B should establish the training structure:

- `trainer_supplied`: the trainer provides an outline that becomes the structural basis.
- `research_assisted`: a future research agent proposes an outline with the trainer.

Person A only records this choice. It does not implement research or generate the outline.

### Output Language

`output_language` applies consistently to the full output set: slides, speaker notes, pre-bite, and post-bite.

- `en`: English
- `nl`: Dutch
- `bilingual`: Dutch and English

### Tier vs Level

`tier` is the challenge scope:

- `1`: Single training
- `2`: Multi-level track
- `3`: Certification programme

`level` is the module depth:

- `1`: Essentials
- `2`: Advanced
- `3`: Expert

Level 1 must have an empty `presupposes` list. Levels 2 and 3 require 3-5 previous concepts.

### Slide Target

The target is `int(duration_hours * 12)`, with a minimum of 30 slides:

- Tier 1: one deck, 30-50 slides
- Tier 2: up to three decks, each targeting 30-50 slides
- Tier 3: larger multi-session output, with each target capped at 80 slides

## Validation Gate

Generation starts only when:

- `validate_intake(data)` returns no issues
- Training Readiness Score is at least 80/100

The score weights are:

| Field | Points |
|---|---:|
| tier | 5 |
| topic | 15 |
| audience | 15 |
| knowledge_level | 10 |
| duration_hours | 10 |
| primary_objective | 25 |
| level | 10 |
| presupposes | 10 |

Validation rejects empty or broad topics/audiences, unsupported knowledge levels, durations outside 0-40 hours, objectives without measurable action verbs, invalid outline/language/tier/level values, incorrect prerequisites, and any changed required constants.

## Orchestration Contract

Person B must add `generate.py` with this interface:

```bash
python generate.py --intake intake.json
```

It must write `content.json`, or clearly print another `.json` output path to stdout.

Person B must use `outline_path` and `output_language` from the intake. The detailed case also requires Person B to generate a visible reliability or confidence indicator per slide so trainers can identify content that needs closer review.

Content generation must be iterative: after the outline is agreed, Person B should propose and generate one logical chunk at a time, such as a theory block or exercise. The trainer confirms or adjusts each chunk before slides are produced. Person A encodes this requirement through `iterative_confirmation_required`; it does not implement the confirmation workflow yet.

Person C must add `render.py` with this interface:

```bash
python render.py --intake intake.json --content content.json
```

It must write:

- `output.pptx`
- `prebite.docx`
- `postbite.docx`

Non-zero subprocess exits and missing expected files become friendly `OrchestratorError` messages. Raw tracebacks are hidden unless `--debug` is used.

The detailed case requires end-to-end API or token cost to be measured and reported for every generated training. Person A encodes this through `cost_tracking_required`; actual cost calculation remains a future pipeline responsibility.

## Dry-Run Demo

```bash
python main.py --dry-run
```

Dry-run still collects, validates, scores, and saves the final intake. It then prints the exact `generate.py` and `render.py` commands without requiring those scripts to exist.

## Shared Slide Contract

`schemas/slides_schema.json` defines Person B's handoff to Person C, including the agreed slide types and all five mandatory speaker-note fields. Person A owns the schema contract but does not generate slide content or render files.

## Maverx Challenge Coverage

This implementation enforces the required didactic arc on the intake contract, requires all five speaker-note fields, distinguishes challenge tier from module level, records level dependencies, requires pre- and post-bites, records outline and language choices, requires future cost/confidence/iterative-confirmation behavior, rejects vague briefs, and provides a timed intake-to-orchestration demo path.

The team-plan PDF describes Tier 2 as three dependent training levels. Person A's schema supports that dependency through `tier`, `level`, and `presupposes`; Person B remains responsible for producing visibly progressive content.

## Person B Deterministic Fallback Generator

Person B provides a reliable demo path that requires no API key, network access, or external Python packages. It generates complete structured JSON content using the existing Maverx slide types from `schemas/slides_schema.json`.

Run:

```bash
python3 generate.py --intake intake.json --output-dir output
```

For Tier 2, the generator always creates:

```text
slides_L1.json              prebite_L1.json
slides_L2.json              prebite_L2.json
slides_L3.json              prebite_L3.json
postbite_L1.json            dataset_spec_L1.json
postbite_L2.json            dataset_spec_L2.json
postbite_L3.json            dataset_spec_L3.json
```

Tier 1 creates only the four Level 1 files. The final CLI line is the absolute path to `slides_L1.json`, allowing Person A's orchestrator to detect the primary output.

### Deck Contract

Each deck contains exactly 20 slides and follows the contiguous order:

```text
kick-off → theory → example → exercise → wrap-up
```

Level 1 contains no Mentimeter recap. Levels 2 and 3 each contain exactly one `mentimeter_recap` slide with five recap questions. Level 2 explicitly builds on Level 1; Level 3 explicitly combines Level 1 and Level 2 concepts.

Every slide includes:

- An existing Maverx `slide_type`
- Short, practical slide content
- A visual suggestion
- Confidence score and reason
- Trainer-ready speaker notes with all required facilitation fields

The deterministic fallback normally scores content at `0.65`, structural slides at `0.75`, and unresearched content requested through a research-assisted outline at `0.50`.

### Language Support

`en`, `nl`, and `bilingual` are supported. Bilingual values remain flat renderable strings:

```text
NL: Nederlandse tekst
EN: English text
```

### Cost Tracking

Every slide deck records estimated input and output tokens. Deterministic fallback generation always reports:

```json
{
  "model_name": "deterministic-fallback",
  "estimated_cost_eur": 0.0
}
```

### Validation

Person B validates every deck and artifact before writing any output. Validation covers slide counts, sequential numbering, block order, allowed slide types, complete speaker notes, confidence fields, level progression, Mentimeter rules, and pre-bite/post-bite/dataset contracts.

Files are written atomically only after the complete requested output set passes validation.

### Person C Handoff

Person C should consume `slides_L{level}.json`, `prebite_L{level}.json`, `postbite_L{level}.json`, and `dataset_spec_L{level}.json`. Person B generates content and render guidance only; it does not create PowerPoint, Word, or Excel files.

## Prototype API

Install the API dependencies and start the local prototype:

```bash
pip install -r requirements.txt
uvicorn api:app --reload --port 8000
```

Endpoints:

- `POST /generate`: validates and scores an intake, then writes Person B JSON artifacts to `./output`.
- `GET /status`: reports whether generated JSON artifacts are available.
- `GET /download/{filename}`: downloads a generated artifact from `./output`.

Example:

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  --data @intake.json
```

The API outputs JSON artifacts for the prototype and for Person C's renderer. It does not render PowerPoint, Word, or Excel files itself.

Bilingual fields remain flat strings so they can be rendered directly:

```text
NL: Nederlandse tekst
EN: English text
```
