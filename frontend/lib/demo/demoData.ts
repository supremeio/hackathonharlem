import type { DeckGroup, DeckResult, PreviewSlide } from "@/types";

/**
 * Canned content for the auto-playing portfolio demo. Everything here is static
 * — the demo never calls the backend, so it deploys as a self-contained site.
 */

/* ── Sidebar history (seeded so the app looks lived-in) ──────────────────── */
export const DEMO_HISTORY: DeckGroup[] = [
  {
    label: "Today",
    decks: [
      { id: "d1", title: "Giving effective feedback to senior staff", updatedAt: "" },
      { id: "d2", title: "Incident response for on-call engineers", updatedAt: "" },
    ],
  },
  {
    label: "Yesterday",
    decks: [
      { id: "d3", title: "Onboarding new hires on our tooling", updatedAt: "" },
      { id: "d4", title: "Data storytelling for analysts", updatedAt: "" },
    ],
  },
  {
    label: "Earlier",
    decks: [
      { id: "d5", title: "Customer discovery interviews 101", updatedAt: "" },
      { id: "d6", title: "Intro to Power BI dashboards", updatedAt: "" },
      { id: "d7", title: "Running effective 1:1s", updatedAt: "" },
    ],
  },
];

/* ── The scripted intake scenario ───────────────────────────────────────── */
export const DEMO_PROMPT =
  "Train our managers on giving effective feedback to senior staff in a 3-hour workshop";

export type DemoStep = {
  kind: "top" | "followup";
  question: string;
  placeholder: string;
  answer: string;
  /** Top-level only: the answer was extracted from the first message → pre-filled. */
  prefilled?: boolean;
  /** Follow-up only: the parent question it hangs under. */
  parent?: string;
};

export const DEMO_STEPS: DemoStep[] = [
  {
    kind: "top",
    question: "What is the topic or skill to be trained?",
    placeholder: "What are you training today",
    prefilled: true,
    answer: "giving effective feedback to senior staff",
  },
  {
    kind: "followup",
    parent: "What is the topic or skill to be trained?",
    question:
      "What specific feedback challenges do these managers struggle with most, for example: delivering tough messages, being too vague, or avoiding the conversation?",
    placeholder: "Type your answer",
    answer: "Delivering tough messages without softening them so much the point is lost",
  },
  {
    kind: "top",
    question: "Who is the target audience?",
    placeholder: "Describe your audience",
    prefilled: true,
    answer: "managers",
  },
  {
    kind: "top",
    question: "What is the knowledge level of participants?",
    placeholder: "e.g. Beginners, Intermediate, Advanced",
    answer: "Intermediate. Experienced managers, new to structured feedback",
  },
  {
    kind: "top",
    question: "How long is the training?",
    placeholder: "e.g. 2 hours, half a day",
    prefilled: true,
    answer: "3 hours",
  },
  {
    kind: "top",
    question: "What is the primary learning objective?",
    placeholder: "By the end, participants will be able to…",
    prefilled: true,
    answer: "give clear, direct feedback to senior staff without softening the message",
  },
];

/** Count of top-level questions (drives the "N of 5" pager). */
export const DEMO_TOTAL = DEMO_STEPS.filter((s) => s.kind === "top").length;

/* ── The generated result (styled preview slides) ───────────────────────── */
const SLIDES: PreviewSlide[] = [
  {
    kind: "cover",
    title: "Giving Effective Feedback to Senior Staff",
    subtitle: "Delivering tough messages clearly, without softening the point",
  },
  {
    kind: "about",
    title: "About this session",
    objectives: [
      "Give clear, direct feedback to senior colleagues",
      "Separate the message from the relationship",
      "Handle defensiveness and push-back calmly",
    ],
    outcomes: [
      "Deliver one real piece of tough feedback by the end",
      "A repeatable structure you can reuse next week",
    ],
    target_group: "Experienced managers, new to structured feedback",
    good_to_know: ["Hands-on and practical", "Built around your real situations"],
  },
  {
    kind: "phases",
    title: "What your day looks like",
    phases: ["Kick-off", "Theory", "Example", "Exercise", "Wrap-up"],
  },
  {
    kind: "agenda",
    title: "Agenda",
    items: [
      "Why feedback to senior staff feels hard, and why it matters",
      "The SBI structure: Situation, Behaviour, Impact",
      "A worked example: softening vs. clarity",
      "Practice: your real feedback, with a partner",
      "Commit: your next conversation",
    ],
  },
  {
    kind: "section",
    title: "1. The cost of softening",
    subtitle: "Theory",
  },
  {
    kind: "theory",
    block: "Theory",
    title: "Why we soften, and what it costs",
    definition:
      "Softening is the instinct to cushion a hard message so much that the point gets lost. With senior staff, status makes the instinct stronger.",
    points: [
      "Clarity is kindness: vagueness wastes everyone's time",
      "Separate the behaviour from the person",
      "Direct is not the same as harsh",
    ],
    statement: "Say the thing. Then help them act on it.",
  },
  {
    kind: "example",
    block: "Example",
    title: "Softening vs. clarity: the same message, two ways",
    scenario:
      "A senior architect keeps overruning design reviews. One manager says 'maybe we could be a bit tighter sometimes'. Another names the pattern, its impact, and a clear ask.",
    points: [
      "The vague version changes nothing",
      "The clear version is specific, calm, and actionable",
    ],
  },
  {
    kind: "exercise",
    block: "Exercise",
    title: "Exercise: deliver it for real",
    fmt: "pair",
    duration_min: 20,
    steps: [
      "Pick a real piece of feedback you've been avoiding",
      "Write it using Situation → Behaviour → Impact",
      "Deliver it to your partner; they play the senior colleague",
      "Swap, then capture what landed and what you'd change",
    ],
    debrief: [
      "What was hardest to say out loud?",
      "Where did you start to soften, and why?",
    ],
  },
  {
    kind: "section",
    title: "Wrap-up & reflection",
    subtitle: "Wrap-up",
  },
  {
    kind: "takeaways",
    title: "Key takeaways",
    items: [
      "Clarity is kindness: say the thing",
      "Situation → Behaviour → Impact keeps it objective",
      "Direct ≠ harsh; calm and specific wins",
    ],
  },
  {
    kind: "closing",
    title: "To close it off",
    reflection: [
      "Who is the one senior colleague you'll give feedback to this week?",
      "What's the first sentence you'll say?",
    ],
  },
];

export const DEMO_RESULT: DeckResult = {
  deckId: "demo",
  title: "Giving Effective Feedback to Senior Staff",
  subtitle: "a 3-hour workshop for managers · intermediate level",
  modelName: "anthropic/claude-sonnet-4.6",
  aiGenerated: true,
  moduleCount: 2,
  pageCount: SLIDES.length,
  durationLabel: "3 hours presentation",
  slides: SLIDES,
  downloads: { pptx: "", prebite: "", postbite: "", plan: "" },
  downloadUrl: null,
};
