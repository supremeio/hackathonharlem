"use client";

import type { Suggestion } from "@/types";

/* === FIGMA DESIGN TOKENS === (node 11:1031 "Options")
   row:  flex flex-wrap content-center gap-10 items-center w-full
   pill: bg white, p-16, rounded-40, flex items-center justify-center
   text: Figtree Medium 14px #0b0825
========================== */
export function SuggestionPills({
  suggestions,
  onSelect,
}: {
  suggestions: Suggestion[];
  onSelect?: (text: string) => void;
}) {
  return (
    <div className="flex w-full flex-wrap content-center items-center gap-[10px]">
      {suggestions.map((s) => (
        <button
          key={s.id}
          type="button"
          onClick={() => onSelect?.(s.text)}
          className="flex items-center justify-center rounded-pill bg-white p-[16px] transition duration-200 hover:bg-[#fafafa] active:scale-[0.98]"
        >
          <span className="whitespace-nowrap text-[15px] font-medium leading-normal text-ink [word-break:break-word]">
            {s.text}
          </span>
        </button>
      ))}
    </div>
  );
}
