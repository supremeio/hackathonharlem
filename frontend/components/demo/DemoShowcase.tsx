"use client";

import { useEffect, useRef, useState } from "react";
import { Sidebar } from "@/components/sidebar/Sidebar";
import { WelcomeHeader } from "@/components/dashboard/WelcomeHeader";
import { BrandLogo } from "@/components/dashboard/BrandLogo";
import { SuggestionPills } from "@/components/dashboard/SuggestionPills";
import { PromptComposer } from "@/components/dashboard/PromptComposer";
import { ChatBubble } from "@/components/flow/ChatBubble";
import { QnATree } from "@/components/flow/QnATree";
import { QuestionCard } from "@/components/flow/QuestionCard";
import { TypingIndicator } from "@/components/flow/TypingIndicator";
import { GenerationStatus } from "@/components/flow/GenerationStatus";
import { ResultPanel } from "@/components/flow/ResultPanel";
import { Spinner } from "@/components/ui/Spinner";
import { DemoCursor } from "@/components/demo/DemoCursor";
import { mockUser, mockModels, mockTiers, mockSuggestions } from "@/lib/api/mock-data";
import {
  DEMO_HISTORY, DEMO_PROMPT, DEMO_STEPS, DEMO_TOTAL, DEMO_RESULT,
} from "@/lib/demo/demoData";
import type { AnswerNode, GenerationStage } from "@/types";

type Phase = "home" | "questions" | "generating" | "result";
const noop = () => {};
const MOVE_MS = 250; // cursor glide duration — keep in sync with DemoCursor's transition

const STAGES = (s: ("done" | "active" | "pending")[]): GenerationStage[] => [
  { id: "analyze", label: "Analyzing your inputs", status: s[0] },
  { id: "generate", label: "Generating slides", status: s[1] },
  { id: "review", label: "Reviewing slides", status: s[2] },
];

/**
 * Auto-playing, looping showcase of the full product flow with a guided cursor.
 * Entirely scripted on canned data — no backend — so it runs as a static site.
 */
export function DemoShowcase() {
  const [phase, setPhase] = useState<Phase>("home");
  const [prompt, setPrompt] = useState("");
  const [initialPrompt, setInitialPrompt] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [nodes, setNodes] = useState<AnswerNode[]>([]);
  const [active, setActive] = useState<
    { question: string; placeholder: string; parent: string | null; prefilled: boolean } | null
  >(null);
  const [draft, setDraft] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [page, setPage] = useState(1);
  const [stages, setStages] = useState<GenerationStage[]>(STAGES(["pending", "pending", "pending"]));
  const [loop, setLoop] = useState(0);
  const [cursor, setCursor] = useState({ x: 720, y: 470, down: false });

  const rootRef = useRef<HTMLDivElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Measure the bottom input block so the conversation scroll keeps 24px clear of it.
  const [bottomEl, setBottomEl] = useState<HTMLDivElement | null>(null);
  const [bottomH, setBottomH] = useState(0);
  useEffect(() => {
    if (!bottomEl) return; // keep the last height through the card↔composer swap
    const update = () => setBottomH(bottomEl.offsetHeight);
    update();
    const ro = new ResizeObserver(update);
    ro.observe(bottomEl);
    return () => ro.disconnect();
  }, [bottomEl]);

  useEffect(() => {
    const alive = { current: true };
    // One speed knob for the whole demo: every pause and typing speed is scaled
    // by SPEED, so a full loop lands around 20s. Lower = faster.
    const SPEED = 0.38;
    const sleep = (ms: number) => new Promise<void>((r) => setTimeout(r, Math.round(ms * SPEED)));
    const rawSleep = (ms: number) => new Promise<void>((r) => setTimeout(r, ms));

    async function type(setter: (v: string) => void, text: string, speed: number) {
      for (let i = 1; i <= text.length; i++) {
        if (!alive.current) return;
        setter(text.slice(0, i));
        await sleep(speed);
      }
    }

    const q = (sel: string) => rootRef.current?.querySelector(sel) as HTMLElement | null;

    async function moveTo(x: number, y: number) {
      setCursor((c) => ({ ...c, x, y }));
      await rawSleep(MOVE_MS); // unscaled — matches the cursor's CSS transition
    }
    async function moveToSel(sel: string) {
      const el = q(sel);
      if (!el) return;
      const r = el.getBoundingClientRect();
      await moveTo(r.left + r.width / 2, r.top + r.height / 2);
    }
    async function click() {
      setCursor((c) => ({ ...c, down: true }));
      await sleep(160);
      setCursor((c) => ({ ...c, down: false }));
      await sleep(150);
    }
    const SEND = 'button[aria-label="Send"], button[aria-label="Submit answer"]';

    // Manual eased scroll-to-top — robust against CSS scroll-behavior and the
    // card→composer resize, which can cancel a native smooth scroll.
    function easeScrollTop(el: HTMLElement, duration = 700) {
      const start = el.scrollTop;
      if (start <= 1) return;
      const t0 = performance.now();
      const frame = (now: number) => {
        if (!alive.current || !el.isConnected) return;
        const p = Math.min(1, (now - t0) / duration);
        el.scrollTop = start * Math.pow(1 - p, 3); // easeOut to 0
        if (p < 1) requestAnimationFrame(frame);
      };
      requestAnimationFrame(frame);
    }

    async function playOnce() {
      // reset
      setPhase("home"); setPrompt(""); setInitialPrompt(""); setAnalyzing(false);
      setNodes([]); setActive(null); setDraft(""); setSubmitting(false); setPage(1);
      setStages(STAGES(["pending", "pending", "pending"]));
      setLoop((n) => n + 1);
      await sleep(900); if (!alive.current) return;

      // 1) move to the composer, click, and type the brief
      await moveToSel('input[placeholder="What are you training today"]'); if (!alive.current) return;
      await click(); if (!alive.current) return;
      await type(setPrompt, DEMO_PROMPT, 30); if (!alive.current) return;
      await sleep(500); if (!alive.current) return;

      // 2) move to send, click → questions + analyzing
      await moveToSel(SEND); if (!alive.current) return;
      await click(); if (!alive.current) return;
      setInitialPrompt(DEMO_PROMPT); setPrompt(""); setPhase("questions");
      setActive(null); setAnalyzing(true);
      await sleep(1900); if (!alive.current) return;
      setAnalyzing(false);

      // 3) walk the scripted intake — every answer is typed
      const built: AnswerNode[] = [];
      let topCount = 0;
      for (const step of DEMO_STEPS) {
        if (!alive.current) return;
        if (step.kind === "top") topCount += 1;
        setPage(Math.max(1, topCount));
        setActive({
          question: step.question,
          placeholder: step.placeholder,
          parent: step.kind === "followup" ? step.parent ?? null : null,
          prefilled: !!step.prefilled,
        });
        setDraft(step.prefilled ? step.answer : ""); // pre-filled answers appear instantly
        await sleep(750); if (!alive.current) return; // let the card animate in

        if (step.prefilled) {
          await sleep(650); if (!alive.current) return; // hold so the pre-fill reads
        } else {
          await moveToSel("input"); if (!alive.current) return;
          await click(); if (!alive.current) return;
          await type(setDraft, step.answer, 24); if (!alive.current) return;
          await sleep(450); if (!alive.current) return;
        }

        // move to send + click → loader, then commit to the thread
        await moveToSel(SEND); if (!alive.current) return;
        await click(); if (!alive.current) return;
        setSubmitting(true);
        await sleep(1000); if (!alive.current) return;
        setSubmitting(false);

        if (step.kind === "top") {
          built.push({ questionId: `q${built.length}`, question: step.question, answer: step.answer, followUps: [] });
        } else if (built.length) {
          built[built.length - 1] = {
            ...built[built.length - 1],
            followUps: [...built[built.length - 1].followUps, { question: step.question, answer: step.answer }],
          };
        }
        setNodes([...built]);
        await sleep(450); if (!alive.current) return;
        // follow the latest answer down the thread
        scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
        await sleep(250); if (!alive.current) return;
      }

      // 4) generating — drift the cursor to centre and rewind the thread to the top
      setActive(null); setDraft(""); setPhase("generating");
      void moveTo(760, 430);
      await sleep(260); if (!alive.current) return; // let the composer swap settle first
      if (scrollRef.current) easeScrollTop(scrollRef.current, 360);
      setStages(STAGES(["active", "pending", "pending"]));
      await sleep(1200); if (!alive.current) return;
      setStages(STAGES(["done", "active", "pending"]));
      await sleep(1300); if (!alive.current) return;
      setStages(STAGES(["done", "done", "active"]));
      await sleep(1300); if (!alive.current) return;
      setStages(STAGES(["done", "done", "done"]));

      // 5) result — slides auto-advance
      setPhase("result");
      await moveTo(1050, 360); if (!alive.current) return;
      await sleep(10500); if (!alive.current) return;
    }

    (async () => {
      while (alive.current) {
        await playOnce();
        if (!alive.current) break;
        await sleep(700);
      }
    })();

    return () => { alive.current = false; };
  }, []);

  const showTree = nodes.length > 0;
  const showComposer = phase === "generating" || phase === "result";

  return (
    <div ref={rootRef} className="relative min-h-screen w-full cursor-none overflow-x-hidden bg-canvas">
      {/* Left sidebar — seeded with history */}
      <div className="absolute left-0 top-0 h-full">
        <Sidebar user={mockUser} deckGroups={DEMO_HISTORY} onCreate={noop} onSelectDeck={noop} />
      </div>

      {/* Centred conversation column */}
      <div className="absolute left-1/2 top-0 h-full w-[680px] -translate-x-1/2">
        <div className="absolute left-0 top-[24px] w-full">
          <WelcomeHeader name={mockUser.name} />
        </div>

        {phase !== "home" && (
          <div className="absolute left-0 top-[160px] flex w-full flex-col gap-[16px]">
            <div className="flex w-full animate-fade-up justify-end">
              <ChatBubble text={initialPrompt} />
            </div>
            {phase === "questions" && analyzing && (
              <div className="flex w-full animate-fade-up justify-start">
                <TypingIndicator />
              </div>
            )}
          </div>
        )}

        {phase === "home" && (
          <div className="absolute bottom-[24px] left-0 flex w-full flex-col items-start gap-[40px]">
            <BrandLogo />
            <div className="flex w-full flex-col items-start gap-[24px]">
              <SuggestionPills suggestions={mockSuggestions} onSelect={noop} />
              <PromptComposer models={mockModels} tiers={mockTiers} value={prompt} onValueChange={noop} onSubmit={noop} />
            </div>
          </div>
        )}

        {/* While analyzing the first message, keep the input visible (it shouldn't
            vanish just because the message bubble is up). */}
        {phase === "questions" && analyzing && (
          <div className="absolute bottom-[24px] left-0 w-full animate-fade-up">
            <PromptComposer models={mockModels} tiers={mockTiers} value="" onValueChange={noop} onSubmit={noop} />
          </div>
        )}

        {showTree && (
          <div
            ref={scrollRef}
            className="no-scrollbar absolute left-0 right-0 top-[225px] overflow-y-auto scroll-smooth"
            style={{ bottom: bottomH + 48 }}
          >
            <QnATree nodes={nodes} />
          </div>
        )}

        {phase === "questions" && !analyzing && active && (
          <div ref={setBottomEl} className="absolute bottom-[24px] left-0 flex w-full animate-fade-up flex-col gap-[8px]">
            <QuestionCard
              heading="Quick questions before we get started"
              question={active.question}
              placeholder={active.placeholder}
              value={draft}
              onChange={noop}
              onSubmit={noop}
              page={page}
              total={DEMO_TOTAL}
              canPrev={false}
              canNext={false}
              onPrev={noop}
              onNext={noop}
              modelName={mockModels[0]?.name ?? "Claude Sonnet 4.6"}
              parentQuestion={active.parent}
              prefilled={active.prefilled}
              loading={submitting}
            />
          </div>
        )}

        {showComposer && (
          <div ref={setBottomEl} className="absolute bottom-[24px] left-0 flex w-full animate-fade-up flex-col items-start gap-[8px]">
            {phase === "generating" && (
              <div className="flex items-center gap-[4px]">
                <Spinner size={20} color="#257498" />
                <span className="whitespace-nowrap text-[15px] font-medium leading-normal text-black">
                  Generating slides
                </span>
              </div>
            )}
            <PromptComposer models={mockModels} tiers={mockTiers} value="" onValueChange={noop} onSubmit={noop} />
          </div>
        )}
      </div>

      {/* Right side: generation status → result */}
      {phase === "generating" && (
        <div className="absolute right-0 top-0 h-full animate-slide-in-right">
          <GenerationStatus stages={stages} />
        </div>
      )}
      {phase === "result" && (
        <>
          <div className="absolute inset-0 animate-fade-in bg-[#25144A]/40" aria-hidden />
          <div key={loop} className="absolute right-0 top-0 h-full animate-slide-in-right">
            <ResultPanel result={DEMO_RESULT} onClose={noop} autoAdvanceMs={750} />
          </div>
        </>
      )}

      {/* Guided cursor overlay */}
      <DemoCursor x={cursor.x} y={cursor.y} down={cursor.down} />
    </div>
  );
}
