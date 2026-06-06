"use client";

import { assets } from "@/lib/assets";

/* === FIGMA DESIGN TOKENS === (node 11:1703 "Create Task")
   bg #f6f6f6, px-16 py-12, rounded-40, flex items-center justify-between, w-full
   label: Figtree SemiBold 14px #0b0825
   icon: system-uicons:create, 24px box (graphic inset within frame)
========================== */
export function CreateButton({ onClick }: { onClick?: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex w-full items-center justify-between rounded-pill bg-surface px-[16px] py-[12px] text-left transition-colors hover:bg-[#efefef]"
    >
      <span className="whitespace-nowrap text-[14px] font-semibold leading-normal text-ink [word-break:break-word]">
        Create new slides
      </span>
      <span className="relative size-[24px] shrink-0 overflow-clip" aria-hidden>
        <span className="absolute inset-[14.47%_14.71%_16.67%_16.67%]">
          <span className="absolute inset-[-3.63%_-3.64%]">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={assets.iconCreate} alt="" className="block size-full max-w-none" />
          </span>
        </span>
      </span>
    </button>
  );
}
