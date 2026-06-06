/**
 * Domain models for the AI Deck Studio.
 * These shapes are intentionally backend-agnostic — the data-access layer in
 * `lib/api` returns exactly these types whether the source is a mock or a live API.
 */

export interface User {
  id: string;
  name: string;
  email: string;
  avatarUrl: string;
  tier: string;
}

export interface Deck {
  id: string;
  title: string;
  /** ISO-8601 timestamp of last activity, used to group decks by day. */
  updatedAt: string;
}

/** Decks grouped into the sidebar's day buckets (Today, Yesterday, ...). */
export interface DeckGroup {
  label: string;
  decks: Deck[];
}

export interface Suggestion {
  id: string;
  text: string;
}

export interface Model {
  id: string;
  name: string;
  iconUrl: string;
}

export interface Tier {
  id: string;
  label: string;
  /** Whether the tier can be selected; unavailable tiers show "Coming soon". */
  available: boolean;
}

/** Payload sent to the backend when the user submits the composer. */
export interface CreateDeckInput {
  prompt: string;
  modelId: string;
  tierId: string;
}

/* ─────────────────────────────────────────────────────────────
   Deck creation flow (frames 2–5)
   ───────────────────────────────────────────────────────────── */

/** One of the fixed interview questions shown after the initial prompt. */
export interface InterviewQuestion {
  id: string;
  text: string;
  placeholder: string;
}

/** An AI-generated follow-up to a top-level question (the indented `↳` row). */
export interface FollowUpQuestion {
  id: string;
  text: string;
  placeholder: string;
}

/** A recorded answer, plus any AI follow-up Q&A gathered for it. */
export interface AnswerNode {
  questionId: string;
  question: string;
  answer: string;
  /** Chained context-gathering sub-questions the AI asked for this answer. */
  followUps: { question: string; answer: string }[];
}

export type StageStatus = "done" | "active" | "pending";

/** A step in the generation status panel (Analyzing → Generating → Reviewing). */
export interface GenerationStage {
  id: string;
  label: string;
  status: StageStatus;
}

/** A preview slide derived from the generated Training plan. `kind` selects the
 *  renderer (cover / about / agenda / theory / example / exercise / …); the rest
 *  of the fields vary by kind. */
export interface PreviewSlide {
  kind: string;
  block?: string;
  title?: string;
  subtitle?: string;
  [key: string]: unknown;
}

export interface DeckDownloads {
  pptx: string;
  prebite: string;
  postbite: string;
  plan: string;
}

/** The generated training returned by the backend once generation completes. */
export interface DeckResult {
  deckId: string;
  title: string;
  subtitle: string;
  modelName: string;
  /** Whether the model actually generated this deck (false = offline template). */
  aiGenerated: boolean;
  moduleCount: number;
  pageCount: number;
  durationLabel: string;
  /** Ordered preview slides (mirror the generated .pptx). */
  slides: PreviewSlide[];
  /** Absolute URLs per artifact. */
  downloads: DeckDownloads;
  /** Convenience: the .pptx URL (the primary "Download slides" target). */
  downloadUrl: string | null;
}

/** Raised when the backend rejects the intake (422); carries the issues. */
export interface ValidationError {
  issues: string[];
  score: number;
}

/** High-level phase of the deck-creation experience. */
export type FlowPhase = "home" | "questions" | "generating" | "result";
