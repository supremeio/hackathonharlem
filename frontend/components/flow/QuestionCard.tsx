"use client";

import { assets } from "@/lib/assets";
import { Icon } from "@/components/ui/Icon";
import { Chevron } from "@/components/ui/Chevron";
import { Spinner } from "@/components/ui/Spinner";

/* === FIGMA DESIGN TOKENS === (node 11:1259 "Questions Container")
   wrapper:  flex col gap-9, w-680
   heading:  Figtree Medium 14px #000
   card:     bg white, border 1px #257498, drop-shadow, p-24, gap-16, rounded-38
   header:   question (Figtree SemiBold 16px #0b0825) + pagination
   pager:    chevron-left 20 / "N of 5" 14px / chevron-right 20  (gap-6)
   field:    bg white, border 1px #257498, drop-shadow, p-20, rounded-16
             caret bar #417499 + input (Figtree Regular 14px/20px #8892a7) + dark send
   footer:   model chip (left) + faded (opacity-10) voice/send group (right)
========================== */
export function QuestionCard({
  heading,
  question,
  placeholder,
  value,
  onChange,
  onSubmit,
  page,
  total,
  canPrev,
  canNext,
  onPrev,
  onNext,
  modelName,
  parentQuestion,
  prefilled,
  loading,
}: {
  heading: string;
  question: string;
  placeholder: string;
  value: string;
  onChange: (v: string) => void;
  onSubmit: () => void;
  page: number;
  total: number;
  canPrev: boolean;
  canNext: boolean;
  onPrev: () => void;
  onNext: () => void;
  modelName: string;
  /** When set, the card is a follow-up: shows a banner with the parent question. */
  parentQuestion?: string | null;
  /** When true, the field was pre-filled from the user's first message. */
  prefilled?: boolean;
  /** When true, the AI is processing the answer — show a loader on the send button. */
  loading?: boolean;
}) {
  const isEmpty = value.trim().length === 0;

  return (
    <div className="flex w-[680px] flex-col gap-[9px]">
      <p className="w-full text-[15px] font-medium leading-normal text-black [word-break:break-word]">
        {heading}
      </p>

      <div className="flex w-full flex-col rounded-[38px] border border-solid border-stroke bg-white">
        {/* Follow-up banner — references the parent question */}
        {parentQuestion && (
          <div className="flex w-full flex-col items-start p-[4px]">
            <div className="flex w-full flex-col items-start justify-center rounded-bl-[4px] rounded-br-[4px] rounded-tl-[34px] rounded-tr-[34px] bg-welcome-bg px-[16px] py-[12px]">
              <div className="flex items-start gap-[4px]">
                <span className="flex shrink-0 items-center justify-center" aria-hidden>
                  <span className="rotate-180">
                    <span className="relative block size-[20px] overflow-clip">
                      <span className="absolute bottom-1/4 left-[20.83%] right-[16.67%] top-1/4">
                        <span className="absolute inset-[-5%_-4%]">
                          {/* eslint-disable-next-line @next/next/no-img-element */}
                          <img
                            src={assets.iconFollowUpArrow}
                            alt=""
                            className="block size-full max-w-none"
                          />
                        </span>
                      </span>
                    </span>
                  </span>
                </span>
                <p className="min-w-0 flex-1 text-[15px] font-medium leading-[20px] text-welcome-ink [overflow-wrap:anywhere]">
                  {parentQuestion}
                </p>
              </div>
            </div>
          </div>
        )}

        <div
          className={`flex w-full flex-col gap-[16px] ${
            parentQuestion ? "px-[24px] pb-[24px] pt-[16px]" : "p-[24px]"
          }`}
        >
          <div className="flex w-full flex-col gap-[20px]">
          {/* Header: question + pagination */}
          <div className="flex w-full items-start justify-between gap-[12px]">
            <p className="min-w-0 flex-1 text-[16px] font-semibold leading-[22px] text-ink [overflow-wrap:anywhere]">
              {question}
            </p>
            <div className="flex shrink-0 items-center gap-[6px]">
              <button
                type="button"
                onClick={onPrev}
                disabled={!canPrev}
                aria-label="Previous question"
                className="transition-transform enabled:hover:scale-110 enabled:active:scale-90 disabled:cursor-default"
              >
                <Chevron direction="left" disabled={!canPrev} />
              </button>
              <p className="whitespace-nowrap text-[15px] font-medium leading-normal text-ink [word-break:break-word]">
                {page} of {total}
              </p>
              <button
                type="button"
                onClick={onNext}
                disabled={!canNext}
                aria-label="Next question"
                className="transition-transform enabled:hover:scale-110 enabled:active:scale-90 disabled:cursor-default"
              >
                <Chevron direction="right" disabled={!canNext} />
              </button>
            </div>
          </div>

          {/* Answer field */}
          <div className="flex w-full items-center justify-between rounded-[16px] border border-solid border-stroke bg-white p-[20px] transition-colors focus-within:border-input-focus">
            <div className="flex flex-1 items-center gap-[8px]">
              <input
                type="text"
                value={value}
                onChange={(e) => onChange(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") onSubmit();
                }}
                placeholder={placeholder}
                autoFocus
                className="h-[24px] min-w-px flex-1 bg-transparent text-[15px] font-normal leading-[24px] text-ink caret-welcome-border outline-none placeholder:text-muted"
              />
            </div>
            <button
              type="button"
              onClick={onSubmit}
              aria-label={loading ? "Processing" : "Submit answer"}
              aria-disabled={isEmpty || loading}
              className={`relative flex size-[32px] shrink-0 items-center justify-center rounded-full transition-[transform,opacity] ${
                loading
                  ? "cursor-wait bg-welcome-bg opacity-100"
                  : `bg-[#25144A] ${isEmpty ? "opacity-30" : "opacity-100 hover:scale-105 active:scale-95"}`
              }`}
            >
              {loading ? (
                <Spinner size={20} color="#25144A" />
              ) : (
                <span className="relative size-[20px] overflow-clip" aria-hidden>
                  <span className="absolute inset-[12.5%_20.83%]">
                    <span className="absolute inset-[-4.67%_-6%]">
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img src={assets.iconArrowUp} alt="" className="block size-full max-w-none" />
                    </span>
                  </span>
                </span>
              )}
            </button>
          </div>

          {/* Pre-fill hint — the answer came from the first message; editable */}
          {prefilled && (
            <div className="flex items-center gap-[6px] text-[13px] font-medium leading-normal text-muted">
              <span className="size-[6px] shrink-0 rounded-full bg-brand-purple" />
              <span className="[word-break:break-word]">
                Pre-filled from your message — edit if needed
              </span>
            </div>
          )}
        </div>

        {/* Footer: model chip + faded voice/send */}
        <div className="flex w-full items-center justify-between">
          <div className="flex items-center gap-[4px] rounded-chip bg-surface px-[8px] py-[4px]">
            <Icon src={assets.iconClaude} size={24} />
            <span className="whitespace-nowrap text-[14px] font-medium leading-normal text-ink [word-break:break-word]">
              {modelName}
            </span>
          </div>
          {/* Decorative voice/send — hidden on follow-up questions */}
          {!parentQuestion && (
            <div className="flex items-center gap-[12px] opacity-10" aria-hidden>
              <Icon src={assets.iconVoice} size={24} />
              <span className="relative flex size-[32px] items-center justify-center rounded-full bg-[#25144A]">
                <span className="relative size-[20px] overflow-clip">
                  <span className="absolute inset-[12.5%_20.83%]">
                    <span className="absolute inset-[-4.67%_-6%]">
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img src={assets.iconArrowUp} alt="" className="block size-full max-w-none" />
                    </span>
                  </span>
                </span>
              </span>
            </div>
          )}
        </div>
        </div>
      </div>
    </div>
  );
}
