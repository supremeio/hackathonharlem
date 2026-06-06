"use client";

import { useEffect, useRef, useState } from "react";
import { assets } from "@/lib/assets";
import { Icon } from "@/components/ui/Icon";
import type { Tier } from "@/types";

/* === FIGMA DESIGN TOKENS === (node 18:58 "Tier dropdown")
   menu:     bg white, border 1px #E2E8F0, rounded-16, p-12, gap-12, w-160 (opens upward)
   item:     rounded-8, px-8 py-4, Figtree Medium 15px/24px #232323
   selected: bg #F3F6F8 + green check (20px)
   tier 2/3: unavailable — hovering swaps the label to "Coming soon"
========================== */
function CheckMark() {
  return (
    <span className="flex size-[20px] shrink-0 items-center justify-center" aria-hidden>
      <svg width={12.67} height={9.33} viewBox="0 0 12.6667 9.33333" fill="none">
        <path
          d="M0.5 5.5L3.83333 8.83333L12.1667 0.5"
          stroke="#008000"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </span>
  );
}

function TierOption({
  tier,
  selected,
  onSelect,
}: {
  tier: Tier;
  selected: boolean;
  onSelect: () => void;
}) {
  const [hover, setHover] = useState(false);
  const comingSoon = !tier.available;
  const label = comingSoon && hover ? "Coming soon" : tier.label;

  return (
    <button
      type="button"
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      onClick={onSelect}
      aria-disabled={comingSoon}
      className={`flex w-full items-center justify-between rounded-[8px] px-[8px] py-[4px] transition-colors ${
        selected ? "bg-[#F3F6F8]" : "bg-white hover:bg-[#F3F6F8]"
      } ${comingSoon ? "cursor-default" : "cursor-pointer"}`}
    >
      <span
        className={`whitespace-nowrap text-[15px] font-medium leading-[24px] [word-break:break-word] ${
          comingSoon ? "text-muted" : "text-[#232323]"
        }`}
      >
        {label}
      </span>
      {selected && <CheckMark />}
    </button>
  );
}

export function TierDropdown({
  tiers,
  selectedId,
  onSelect,
}: {
  tiers: Tier[];
  selectedId: string;
  onSelect: (id: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const selected = tiers.find((t) => t.id === selectedId) ?? tiers[0];

  useEffect(() => {
    if (!open) return;
    const onDoc = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, [open]);

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-haspopup="listbox"
        aria-expanded={open}
        className="flex items-center gap-[4px] transition-opacity hover:opacity-70"
      >
        <span className="flex items-center gap-[4px]">
          <Icon src={assets.iconAiScan} size={20} />
          <span className="whitespace-nowrap text-[12px] font-medium leading-normal text-ink [word-break:break-word]">
            {selected?.label}
          </span>
        </span>
        <Icon
          src={assets.iconChevronDown}
          size={16}
          className={`transition-transform ${open ? "rotate-180" : ""}`}
        />
      </button>

      {open && (
        <div
          role="listbox"
          className="absolute bottom-full left-0 z-50 mb-[8px] flex w-[160px] origin-bottom-left animate-pop flex-col gap-[12px] rounded-[16px] border border-solid border-stroke bg-white p-[12px]"
        >
          {tiers.map((tier) => (
            <TierOption
              key={tier.id}
              tier={tier}
              selected={tier.id === selectedId}
              onSelect={() => {
                if (tier.available) {
                  onSelect(tier.id);
                  setOpen(false);
                }
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}
