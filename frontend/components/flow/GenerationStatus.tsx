import { StageIcon } from "@/components/ui/StageIcon";
import type { GenerationStage } from "@/types";

/* === FIGMA DESIGN TOKENS === (node 7:878 "Sidebar" / process list)
   outer: bg #f6f6f6, w-331, p-16; card: bg white rounded-24 p-24
   steps: flex col gap-24; item: gap-4 items-center → icon 20 + label
   label: Figtree Medium 14px/1.4 #0b0825
========================== */
export function GenerationStatus({ stages }: { stages: GenerationStage[] }) {
  return (
    <aside className="flex h-full w-[331px] flex-col items-start bg-canvas p-[16px]">
      <div className="flex w-full flex-col items-start rounded-card bg-white p-[24px]">
        <div className="flex w-full flex-col items-start gap-[24px]">
          {stages.map((stage) => (
            <div key={stage.id} className="flex w-full items-center gap-[4px]">
              <StageIcon status={stage.status} size={20} />
              <p className="whitespace-nowrap text-[15px] font-medium leading-[1.4] text-ink [word-break:break-word]">
                {stage.label}
              </p>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
}
