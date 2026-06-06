"use client";

import { useState } from "react";
import { assets } from "@/lib/assets";
import { Icon } from "@/components/ui/Icon";
import { TierDropdown } from "./TierDropdown";
import type { CreateDeckInput, Model, Tier } from "@/types";

/* === FIGMA DESIGN TOKENS === (node 11:996 "Selection Container")
   card:  bg white, border 1px solid #257498, drop-shadow 0 0 1px rgba(0,0,0,.1)
          rounded-23, pt-40 pb-24 px-24, flex col gap-24, w-full
   caret: vertical 24px line #417499 (0.5px)
   input placeholder: Figtree Regular 14px/20px #8892a7
   model chip: bg #f6f6f6, px-8 py-4, rounded-400, gap-4 → icon 24 + label 14px
   tier: ai-scan 20 + "Tier 1" 12px + chevron 16
   voice icon 24; send: 32px circle #25144A + arrow-up 20
========================== */
export function PromptComposer({
  models,
  tiers,
  value,
  onValueChange,
  onSubmit,
}: {
  models: Model[];
  tiers: Tier[];
  value: string;
  onValueChange: (value: string) => void;
  onSubmit?: (input: CreateDeckInput) => void;
}) {
  const [modelId] = useState(models[0]?.id ?? "");
  const [tierId, setTierId] = useState(tiers[0]?.id ?? "");

  const activeModel = models.find((m) => m.id === modelId) ?? models[0];

  const isEmpty = value.trim().length === 0;

  function submit() {
    if (isEmpty) return;
    onSubmit?.({ prompt: value.trim(), modelId, tierId });
    onValueChange("");
  }

  return (
    <div className="flex w-full flex-col gap-[24px] rounded-input border border-solid border-stroke bg-white px-[24px] pb-[24px] pt-[40px] transition-colors focus-within:border-input-focus">
      {/* Prompt row */}
      <div className="flex w-full items-center gap-[8px]">
        <input
          type="text"
          value={value}
          onChange={(e) => onValueChange(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") submit();
          }}
          placeholder="What are you training today"
          className="h-[24px] min-w-px flex-1 bg-transparent text-[15px] font-normal leading-[24px] text-ink caret-welcome-border outline-none placeholder:font-normal placeholder:text-muted"
        />
      </div>

      {/* Controls row */}
      <div className="flex w-full items-center justify-between">
        <div className="flex items-center gap-[16px]">
          {/* Model chip */}
          <button
            type="button"
            className="flex items-center gap-[4px] rounded-chip bg-surface px-[8px] py-[4px]"
          >
            <Icon src={activeModel?.iconUrl ?? assets.iconClaude} size={24} />
            <span className="whitespace-nowrap text-[14px] font-medium leading-normal text-ink [word-break:break-word]">
              {activeModel?.name}
            </span>
          </button>

          {/* Tier selector */}
          <TierDropdown tiers={tiers} selectedId={tierId} onSelect={setTierId} />
        </div>

        {/* Voice + send */}
        <div className="flex items-center gap-[12px]">
          <button
            type="button"
            aria-label="Voice input (coming soon)"
            disabled
            title="Coming soon"
            className="cursor-not-allowed"
          >
            <Icon src={assets.iconVoice} size={24} />
          </button>
          <button
            type="button"
            onClick={submit}
            aria-label="Send"
            aria-disabled={isEmpty}
            className={`relative flex size-[32px] shrink-0 items-center justify-center rounded-full bg-[#25144A] transition-[transform,opacity] hover:scale-105 active:scale-95 ${
              isEmpty ? "opacity-30" : "opacity-100"
            }`}
          >
            <span className="relative size-[20px] overflow-clip" aria-hidden>
              <span className="absolute inset-[12.5%_20.83%]">
                <span className="absolute inset-[-4.67%_-6%]">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={assets.iconArrowUp} alt="" className="block size-full max-w-none" />
                </span>
              </span>
            </span>
          </button>
        </div>
      </div>
    </div>
  );
}
