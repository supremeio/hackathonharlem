"use client";

import { useCallback, useEffect, useState } from "react";
import { Sidebar } from "@/components/sidebar/Sidebar";
import { WelcomeHeader } from "./WelcomeHeader";
import { BrandLogo } from "./BrandLogo";
import { SuggestionPills } from "./SuggestionPills";
import { PromptComposer } from "./PromptComposer";
import { useDeckFlow } from "./useDeckFlow";
import { ChatBubble } from "@/components/flow/ChatBubble";
import { QnATree } from "@/components/flow/QnATree";
import { QuestionCard } from "@/components/flow/QuestionCard";
import { GenerationStatus } from "@/components/flow/GenerationStatus";
import { ResultPanel } from "@/components/flow/ResultPanel";
import { Spinner } from "@/components/ui/Spinner";
import { getDeckById, getDeckGroups } from "@/lib/api";
import type { DeckGroup, Model, Suggestion, Tier, User } from "@/types";

function tierNumber(tierId?: string): number {
  const n = Number((tierId ?? "").replace("tier-", ""));
  return Number.isFinite(n) && n > 0 ? n : 1;
}

/**
 * Top-level interactive shell. Renders the sidebar + centred conversation column
 * and switches between the four flow phases (home → questions → generating →
 * result), driven by `useDeckFlow`.
 */
export function DashboardView({
  user,
  deckGroups,
  suggestions,
  models,
  tiers,
}: {
  user: User;
  deckGroups: DeckGroup[];
  suggestions: Suggestion[];
  models: Model[];
  tiers: Tier[];
}) {
  const flow = useDeckFlow();
  const [homePrompt, setHomePrompt] = useState("");
  const [composerDraft, setComposerDraft] = useState("");
  const [resultClosed, setResultClosed] = useState(false);
  const [resultClosing, setResultClosing] = useState(false);
  const [groups, setGroups] = useState<DeckGroup[]>(deckGroups);

  const refreshHistory = useCallback(async () => {
    setGroups(await getDeckGroups());
  }, []);

  useEffect(() => {
    void refreshHistory();
  }, [refreshHistory]);

  // A fresh result means a new deck was saved — refresh the sidebar.
  useEffect(() => {
    if (flow.phase === "result") {
      setResultClosed(false);
      setResultClosing(false);
      void refreshHistory();
    }
  }, [flow.phase, flow.result, refreshHistory]);

  function closeResult() {
    setResultClosing(true);
    setTimeout(() => {
      setResultClosed(true);
      setResultClosing(false);
    }, 300);
  }

  async function handleSelectDeck(deckId: string) {
    const deck = await getDeckById(deckId);
    if (deck) flow.showResult(deck);
  }

  const showTree = flow.answeredNodes.length > 0;
  const showComposer = flow.phase === "generating" || flow.phase === "result";

  return (
    <div className="relative min-h-screen w-full overflow-x-hidden bg-canvas">
      {/* Left sidebar */}
      <div className="absolute left-0 top-0 h-full">
        <Sidebar
          user={user}
          deckGroups={groups}
          onCreate={() => window.location.reload()}
          onSelectDeck={handleSelectDeck}
        />
      </div>

      {/* Centred conversation column (680px) */}
      <div className="absolute left-1/2 top-0 h-full w-[680px] -translate-x-1/2">
        <div className="absolute left-0 top-[24px] w-full">
          <WelcomeHeader name={user.name} />
        </div>

        {flow.phase !== "home" && (
          <div className="absolute left-0 top-[160px] flex w-full animate-fade-up justify-end">
            <ChatBubble text={flow.initialPrompt} />
          </div>
        )}

        {/* Home: logo + suggestions + composer (bottom-anchored) */}
        {flow.phase === "home" && (
          <div className="absolute bottom-[24px] left-0 flex w-full flex-col items-start gap-[40px]">
            <BrandLogo />
            <div className="flex w-full flex-col items-start gap-[24px]">
              <SuggestionPills suggestions={suggestions} onSelect={setHomePrompt} />
              <PromptComposer
                models={models}
                tiers={tiers}
                value={homePrompt}
                onValueChange={setHomePrompt}
                onSubmit={(input) => flow.start(input.prompt, tierNumber(input.tierId))}
              />
            </div>
          </div>
        )}

        {/* Progressive Q&A tree */}
        {showTree && (
          <div
            className={`absolute left-0 top-[225px] overflow-y-auto pr-[8px] ${
              flow.phase === "questions"
                ? "max-h-[calc(100vh-540px)]"
                : "max-h-[calc(100vh-437px)]"
            }`}
          >
            <QnATree nodes={flow.answeredNodes} />
          </div>
        )}

        {/* Questions: error banner + bottom question card */}
        {flow.phase === "questions" && flow.activeQuestion && (
          <div className="absolute bottom-[24px] left-0 flex w-full animate-fade-up flex-col gap-[8px]">
            {flow.error && (
              <div className="flex w-full flex-col gap-[2px] rounded-[16px] border border-solid border-[#E2B8B8] bg-[#FDF3F3] px-[16px] py-[12px]">
                <p className="text-[14px] font-semibold text-[#8A2C2C]">
                  Let&rsquo;s refine a couple of answers
                </p>
                {flow.error.issues.slice(0, 4).map((issue, i) => (
                  <p key={i} className="text-[13px] leading-[18px] text-[#A85454]">
                    {issue}
                  </p>
                ))}
              </div>
            )}
            <QuestionCard
              heading="Quick questions before we get started"
              question={flow.activeQuestion.text}
              placeholder={flow.activeQuestion.placeholder}
              value={flow.draft}
              onChange={(v) => {
                if (flow.error) flow.clearError();
                flow.setDraft(v);
              }}
              onSubmit={flow.submitDraft}
              page={flow.page}
              total={flow.total}
              canPrev={flow.canPrev}
              canNext={flow.canNext}
              onPrev={flow.goPrev}
              onNext={flow.goNext}
              modelName={models[0]?.name ?? "Claude Sonnet 4.6"}
              parentQuestion={flow.parentQuestion}
            />
          </div>
        )}

        {/* Generating / Result: status label + full composer (bottom-anchored) */}
        {showComposer && (
          <div className="absolute bottom-[24px] left-0 flex w-full animate-fade-up flex-col items-start gap-[8px]">
            {flow.phase === "generating" && (
              <div className="flex items-center gap-[4px]">
                <Spinner size={20} color="#257498" />
                <span className="whitespace-nowrap text-[15px] font-medium leading-normal text-black">
                  Generating slides
                </span>
              </div>
            )}
            <PromptComposer
              models={models}
              tiers={tiers}
              value={composerDraft}
              onValueChange={setComposerDraft}
              onSubmit={() => setComposerDraft("")}
            />
          </div>
        )}
      </div>

      {/* Right side: generation status (generating) → presentation (result) */}
      {flow.phase === "generating" && (
        <div className="absolute right-0 top-0 h-full animate-slide-in-right">
          <GenerationStatus stages={flow.stages} />
        </div>
      )}
      {flow.phase === "result" && flow.result && !resultClosed && (
        <>
          <div
            className={`absolute inset-0 bg-[#25144A]/40 ${
              resultClosing ? "animate-fade-out" : "animate-fade-in"
            }`}
            onClick={closeResult}
            aria-hidden
          />
          <div
            className={`absolute right-0 top-0 h-full ${
              resultClosing ? "animate-slide-out-right" : "animate-slide-in-right"
            }`}
          >
            <ResultPanel result={flow.result} onClose={closeResult} />
          </div>
        </>
      )}
    </div>
  );
}
