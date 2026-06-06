import type {
  AnswerNode,
  DeckGroup,
  DeckResult,
  FollowUpQuestion,
  InterviewQuestion,
  Model,
  Suggestion,
  Tier,
  User,
} from "@/types";
import {
  mockModels,
  mockQuestions,
  mockSuggestions,
  mockTiers,
  mockUser,
} from "./mock-data";

/**
 * Data-access layer. UI components only ever call these functions.
 *
 * Identity, suggestions, models, tiers and the interview script stay client-side
 * (they're fixed); deck generation and history go to the FastAPI backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

function resolve<T>(value: T): Promise<T> {
  return Promise.resolve(value);
}

export async function getCurrentUser(): Promise<User> {
  return resolve(mockUser);
}

export async function getSuggestions(): Promise<Suggestion[]> {
  return resolve(mockSuggestions);
}

export async function getModels(): Promise<Model[]> {
  return resolve(mockModels);
}

export async function getTiers(): Promise<Tier[]> {
  return resolve(mockTiers);
}

export async function getInterviewQuestions(
  _prompt: string,
): Promise<InterviewQuestion[]> {
  return resolve(mockQuestions);
}

/**
 * Extract any intake answers already present in the user's first message, keyed
 * by the bare field name (topic, audience, level, duration, objective). Used to
 * pre-fill the matching questions. Returns {} on any failure (no pre-fill).
 */
export async function extractIntake(
  message: string,
): Promise<Record<string, string>> {
  try {
    const res = await fetch(`${API_BASE}/intake/extract`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    if (!res.ok) return {};
    const data = await res.json();
    const fields = (data?.fields ?? {}) as Record<string, unknown>;
    const out: Record<string, string> = {};
    for (const [k, v] of Object.entries(fields)) {
      const s = String(v ?? "").trim();
      if (s) out[k] = s;
    }
    return out;
  } catch {
    return {};
  }
}

/**
 * Ask the backend whether the AI needs more context for `key`. Returns the next
 * follow-up sub-question, or null when there's enough context (or the cap is hit).
 */
export async function getFollowUp(params: {
  key: string;
  answers: Record<string, string>;
  thread: { question: string; answer: string }[];
}): Promise<FollowUpQuestion | null> {
  try {
    const res = await fetch(`${API_BASE}/intake/followup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });
    if (!res.ok) return null;
    const data = await res.json();
    if (!data.followup) return null;
    return {
      id: `${params.key}_f${params.thread.length + 1}`,
      text: String(data.followup),
      placeholder: "Type your answer",
    };
  } catch {
    return null;
  }
}

/* ── Backend-backed calls ─────────────────────────────────────────────── */

/** Deck history grouped Today / Yesterday / Earlier. Empty on any failure. */
export async function getDeckGroups(): Promise<DeckGroup[]> {
  try {
    const res = await fetch(`${API_BASE}/decks`, { cache: "no-store" });
    if (!res.ok) return [];
    const data = await res.json();
    return (data.groups ?? []) as DeckGroup[];
  } catch {
    return [];
  }
}

/** Load a previously generated deck (history click). */
export async function getDeckById(id: string): Promise<DeckResult | null> {
  try {
    const res = await fetch(`${API_BASE}/decks/${id}`, { cache: "no-store" });
    if (!res.ok) return null;
    return mapPayload(await res.json());
  } catch {
    return null;
  }
}

/** Build the deck: maps the interview answers, POSTs to the backend. */
export async function generateDeck(answers: AnswerNode[]): Promise<DeckResult> {
  const res = await fetch(`${API_BASE}/decks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(buildAnswers(answers)),
  });

  if (res.status === 422) {
    const data = await res.json().catch(() => ({}));
    const detail = data?.detail ?? {};
    const err = new Error("Intake did not pass validation.") as Error & {
      validation?: { issues: string[]; score: number };
    };
    err.validation = { issues: detail.issues ?? [], score: detail.score ?? 0 };
    throw err;
  }
  if (res.status === 502) {
    const data = await res.json().catch(() => ({}));
    throw new Error(
      data?.detail?.message ??
        "The AI model failed to generate this training. Please try again.",
    );
  }
  if (!res.ok) {
    throw new Error(`Generation failed (${res.status}).`);
  }
  return mapPayload(await res.json());
}

/* ── helpers ──────────────────────────────────────────────────────────── */

function abs(url: unknown): string | null {
  return url ? `${API_BASE}${url}` : null;
}

function mapPayload(d: Record<string, any>): DeckResult {
  const dl = d.downloads ?? {};
  return {
    deckId: String(d.deck_id ?? ""),
    title: String(d.title ?? "Untitled training"),
    subtitle: String(d.subtitle ?? ""),
    modelName: String(d.model_name ?? ""),
    aiGenerated: Boolean(d.ai_generated),
    moduleCount: Number(d.module_count ?? 0),
    pageCount: Number(d.page_count ?? 0),
    durationLabel: String(d.duration_label ?? ""),
    slides: (d.slides ?? []) as DeckResult["slides"],
    downloads: {
      pptx: abs(dl.pptx) ?? "",
      prebite: abs(dl.prebite) ?? "",
      postbite: abs(dl.postbite) ?? "",
      plan: abs(dl.plan) ?? "",
    },
    downloadUrl: abs(d.download_url),
  };
}

/** Fold an answer's follow-up Q&A into one enriched string for the planner. */
function enriched(node?: AnswerNode): string {
  if (!node) return "";
  const extra = (node.followUps ?? [])
    .map((f) => `${f.question} ${f.answer}`)
    .join("; ");
  return extra ? `${node.answer}. ${extra}` : node.answer;
}

function buildAnswers(nodes: AnswerNode[]) {
  const byId = Object.fromEntries(nodes.map((n) => [n.questionId, n]));
  return {
    // topic/audience/objective carry the gathered context; level/duration stay clean.
    topic: enriched(byId["q_topic"]),
    audience: enriched(byId["q_audience"]),
    level: byId["q_level"]?.answer ?? "",
    duration: byId["q_duration"]?.answer ?? "",
    objective: enriched(byId["q_objective"]),
  };
}

export { API_BASE };
