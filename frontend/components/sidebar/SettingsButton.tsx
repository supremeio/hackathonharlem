"use client";

import { assets } from "@/lib/assets";

/* === FIGMA DESIGN TOKENS === (node 11:1739 "Settings Container")
   bg white, px-16 py-12, rounded-16, flex items-center justify-between, w-full
   label: Figtree Medium 14px #0b0825
   icon: solar:settings-outline, 24px box (graphic inset within frame)
========================== */
export function SettingsButton({ onClick }: { onClick?: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex w-full items-center justify-between rounded-[16px] bg-white px-[16px] py-[12px] text-left transition-colors hover:bg-surface"
    >
      <span className="whitespace-nowrap text-[14px] font-medium leading-normal text-ink [word-break:break-word]">
        Settings
      </span>
      <span className="relative size-[24px] shrink-0 overflow-clip" aria-hidden>
        <span className="absolute inset-[5.21%_7.59%]">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={assets.iconSettings} alt="" className="absolute inset-0 block size-full max-w-none" />
        </span>
      </span>
    </button>
  );
}
