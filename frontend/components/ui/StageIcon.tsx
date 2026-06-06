import type { StageStatus } from "@/types";
import { Spinner } from "./Spinner";

/* === FIGMA === status glyph in the generation panel.
   done → green check (#008000); active/pending → spinner (#DDD2A3). */
export function StageIcon({
  status,
  size = 20,
}: {
  status: StageStatus;
  size?: number;
}) {
  if (status === "done") {
    // Check glyph (node 243:3992): viewBox 12.67×9.33, stroke #008000.
    const w = (size / 20) * 12.67;
    const h = (size / 20) * 9.33;
    return (
      <span
        className="relative flex shrink-0 items-center justify-center"
        style={{ width: size, height: size }}
        aria-hidden
      >
        <svg width={w} height={h} viewBox="0 0 12.6667 9.33333" fill="none">
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
  // Active and pending both render the spinner; the active one reads as "in progress".
  return <Spinner size={size} color="#DDD2A3" />;
}
