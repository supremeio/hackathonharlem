"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { generateDeck, getFollowUp, getInterviewQuestions } from "@/lib/api";
import type {
  AnswerNode,
  DeckResult,
  FollowUpQuestion,
  FlowPhase,
  GenerationStage,
  InterviewQuestion,
} from "@/types";

const INITIAL_STAGES: GenerationStage[] = [
  { id: "analyze", label: "Analyzing your inputs", status: "pending" },
  { id: "generate", label: "Generating slides", status: "pending" },
  { id: "review", label: "Reviewing slides", status: "pending" },
];

/**
 * Drives the deck-creation experience across its four phases. All backend touch
 * points go through `lib/api`, so swapping mocks for live calls (including
 * streaming generation events) only changes this hook — not the views.
 */
export function useDeckFlow() {
  const [phase, setPhase] = useState<FlowPhase>("home");
  const [initialPrompt, setInitialPrompt] = useState("");

  const [questions, setQuestions] = useState<InterviewQuestion[]>([]);
  const [index, setIndex] = useState(0);
  const [maxReached, setMaxReached] = useState(0);
  const [answers, setAnswers] = useState<Record<string, AnswerNode>>({});
  const [pendingFollowUp, setPendingFollowUp] = useState<FollowUpQuestion | null>(null);
  const [draft, setDraft] = useState("");

  const [stages, setStages] = useState<GenerationStage[]>(INITIAL_STAGES);
  const [result, setResult] = useState<DeckResult | null>(null);
  const [error, setError] = useState<{ issues: string[]; score: number } | null>(null);

  const tierRef = useRef(1);
  const timers = useRef<ReturnType<typeof setTimeout>[]>([]);
  useEffect(() => () => timers.current.forEach(clearTimeout), []);

  const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));

  /** Ordered answers for the tree (memoised so its identity is stable across
   *  renders — otherwise consumers that depend on it in effects would loop). */
  const answeredNodes: AnswerNode[] = useMemo(
    () => questions.map((q) => answers[q.id]).filter(Boolean) as AnswerNode[],
    [questions, answers],
  );

  const current = questions[index];

  const start = useCallback(async (prompt: string, tier: number = 1) => {
    tierRef.current = tier;
    setError(null);
    setInitialPrompt(prompt);
    const qs = await getInterviewQuestions(prompt);
    setQuestions(qs);
    setIndex(0);
    setMaxReached(0);
    setAnswers({});
    setPendingFollowUp(null);
    setDraft("");
    setPhase("questions");
  }, []);

  const runGeneration = useCallback(async (finalAnswers: AnswerNode[]) => {
    setError(null);
    setPhase("generating");
    timers.current.forEach(clearTimeout);
    setStages([
      { id: "analyze", label: "Analyzing your inputs", status: "active" },
      { id: "generate", label: "Generating slides", status: "pending" },
      { id: "review", label: "Reviewing slides", status: "pending" },
    ]);

    const at = (ms: number, fn: () => void) => timers.current.push(setTimeout(fn, ms));
    at(1000, () =>
      setStages([
        { id: "analyze", label: "Analyzing your inputs", status: "done" },
        { id: "generate", label: "Generating slides", status: "active" },
        { id: "review", label: "Reviewing slides", status: "pending" },
      ]),
    );
    at(2200, () =>
      setStages([
        { id: "analyze", label: "Analyzing your inputs", status: "done" },
        { id: "generate", label: "Generating slides", status: "done" },
        { id: "review", label: "Reviewing slides", status: "active" },
      ]),
    );

    try {
      // Real work runs in parallel with a minimum dwell so the stages are visible.
      const [deck] = await Promise.all([
        generateDeck(finalAnswers),
        delay(2600),
      ]);
      timers.current.forEach(clearTimeout);
      setStages((s) => s.map((stage) => ({ ...stage, status: "done" as const })));
      setResult(deck);
      setPhase("result");
    } catch (err) {
      timers.current.forEach(clearTimeout);
      const validation = (err as { validation?: { issues: string[]; score: number } }).validation;
      setError(
        validation ?? { issues: [(err as Error).message || "Generation failed."], score: 0 },
      );
      setPhase("questions");
    }
  }, []);

  /** Show a previously generated deck (history click). */
  const showResult = useCallback((deck: DeckResult) => {
    setError(null);
    setResult(deck);
    setInitialPrompt(deck.title);
    setPhase("result");
  }, []);

  const advance = useCallback(
    (latest: Record<string, AnswerNode>) => {
      if (index < questions.length - 1) {
        const next = index + 1;
        setIndex(next);
        setMaxReached((m) => Math.max(m, next));
        setDraft(answers[questions[next]?.id]?.answer ?? "");
      } else {
        const ordered = questions
          .map((q) => latest[q.id])
          .filter(Boolean) as AnswerNode[];
        void runGeneration(ordered);
      }
    },
    [index, questions, answers, runGeneration],
  );

  /** Ask the backend whether the AI needs more context for this question. */
  const requestFollowUp = useCallback(
    (q: InterviewQuestion, answersMap: Record<string, AnswerNode>) => {
      const key = q.id.replace(/^q_/, "");
      const topLevel: Record<string, string> = {};
      for (const qq of questions) {
        const node = answersMap[qq.id];
        if (node) topLevel[qq.id.replace(/^q_/, "")] = node.answer;
      }
      const thread = answersMap[q.id]?.followUps ?? [];
      return getFollowUp({ key, answers: topLevel, thread });
    },
    [questions],
  );

  const submitDraft = useCallback(async () => {
    const text = draft.trim();
    if (!text || !current) return;

    // Answering a pending follow-up → append it, then ask if more context is needed.
    if (pendingFollowUp) {
      const node = answers[current.id];
      const updated: Record<string, AnswerNode> = {
        ...answers,
        [current.id]: {
          ...node,
          followUps: [...(node?.followUps ?? []), { question: pendingFollowUp.text, answer: text }],
        },
      };
      setAnswers(updated);
      setDraft("");
      const next = await requestFollowUp(current, updated);
      setPendingFollowUp(next);
      if (!next) advance(updated);
      return;
    }

    // Record the top-level answer, then let the AI decide on follow-ups.
    const node: AnswerNode = {
      questionId: current.id,
      question: current.text,
      answer: text,
      followUps: [],
    };
    const updated = { ...answers, [current.id]: node };
    setAnswers(updated);
    setDraft("");

    const next = await requestFollowUp(current, updated);
    setPendingFollowUp(next);
    if (!next) advance(updated);
  }, [draft, current, pendingFollowUp, answers, advance, requestFollowUp]);

  const goPrev = useCallback(() => {
    if (index === 0) return;
    const prev = index - 1;
    setPendingFollowUp(null);
    setIndex(prev);
    setDraft(answers[questions[prev]?.id]?.answer ?? "");
  }, [index, answers, questions]);

  const goNext = useCallback(() => {
    if (index >= maxReached) return;
    const next = index + 1;
    setPendingFollowUp(null);
    setIndex(next);
    setDraft(answers[questions[next]?.id]?.answer ?? "");
  }, [index, maxReached, answers, questions]);

  // What the question card should currently display.
  const activeQuestion = pendingFollowUp
    ? { text: pendingFollowUp.text, placeholder: pendingFollowUp.placeholder }
    : current
      ? { text: current.text, placeholder: current.placeholder }
      : null;

  return {
    phase,
    initialPrompt,
    questions,
    answeredNodes,
    stages,
    result,
    draft,
    setDraft,
    activeQuestion,
    // The parent question when the card is showing an AI follow-up.
    parentQuestion: pendingFollowUp && current ? current.text : null,
    page: index + 1,
    total: questions.length,
    canPrev: index > 0,
    canNext: index < maxReached,
    start,
    submitDraft,
    goPrev,
    goNext,
    error,
    clearError: () => setError(null),
    showResult,
  };
}
