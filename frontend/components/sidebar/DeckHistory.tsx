"use client";

import { Fragment } from "react";
import type { DeckGroup } from "@/types";

/* === FIGMA DESIGN TOKENS === (node 11:1711 "Task List Container")
   container: flex col gap-24, px-16, w-full
   group:     flex col gap-8, w-full
   label:     Figtree Medium 14px #8892a7 uppercase
   item:      flex items-center py-8 w-full
   item text: Figtree Medium 14px/20px #0b0825
   divider:   1px line #F2F2F2, full width
========================== */
/* === FIGMA === empty state (node 11:10880): slider-placeholder glyph (#8892a7 @30%)
   + "Your slide history is shown here" caption, centred. */
function EmptyHistory() {
  return (
    <div className="flex w-full flex-col items-center gap-[4px] px-[16px] pt-[8px]">
      <svg
        viewBox="0 0 192 168"
        className="w-[150px]"
        fill="none"
        aria-hidden
      >
        <line x1="14" y1="6" x2="178" y2="6" stroke="#8892A7" strokeOpacity="0.3" strokeWidth="3" strokeLinecap="round" />
        <rect x="6" y="34" width="180" height="100" rx="34" stroke="#8892A7" strokeOpacity="0.3" strokeWidth="3" />
        <line x1="14" y1="162" x2="178" y2="162" stroke="#8892A7" strokeOpacity="0.3" strokeWidth="3" strokeLinecap="round" />
      </svg>
      <p className="w-[183px] text-center text-[14px] font-medium leading-normal text-muted [word-break:break-word]">
        Your slide history is shown here
      </p>
    </div>
  );
}

export function DeckHistory({
  groups,
  onSelect,
}: {
  groups: DeckGroup[];
  onSelect?: (deckId: string) => void;
}) {
  if (groups.length === 0) {
    return <EmptyHistory />;
  }

  return (
    <div className="flex w-full flex-col gap-[24px] px-[16px]">
      {groups.map((group, index) => (
        <Fragment key={group.label}>
          {index > 0 && <div className="h-px w-full bg-stroke" />}
          <div className="flex w-full flex-col gap-[8px]">
            <p className="w-full text-[14px] font-medium uppercase leading-normal text-muted [word-break:break-word]">
              {group.label}
            </p>
            {group.decks.length > 0 && (
              <div className="flex w-full flex-col items-start">
                {group.decks.map((deck) => (
                  <button
                    key={deck.id}
                    type="button"
                    onClick={() => onSelect?.(deck.id)}
                    className="flex w-full items-center py-[8px] text-left"
                  >
                    <span className="block w-full truncate text-[14px] font-medium leading-[20px] text-ink transition-colors hover:text-muted">
                      {deck.title}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </Fragment>
      ))}
    </div>
  );
}
