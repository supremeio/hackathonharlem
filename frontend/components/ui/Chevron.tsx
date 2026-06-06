/* === FIGMA === pagination chevron (node 7:251 / 7:257)
   viewBox 6.2×11.2, stroke #0B0825 width 1.2, round. Faded (0.2 opacity) when disabled. */
export function Chevron({
  direction,
  disabled = false,
  size = 20,
}: {
  direction: "left" | "right";
  disabled?: boolean;
  size?: number;
}) {
  const d =
    direction === "left" ? "M5.6 0.6L0.6 5.6L5.6 10.6" : "M0.6 0.6L5.6 5.6L0.6 10.6";
  return (
    <span
      className="relative flex shrink-0 items-center justify-center"
      style={{ width: size, height: size }}
      aria-hidden
    >
      <svg width={6.2} height={11.2} viewBox="0 0 6.2 11.2" fill="none">
        <path
          d={d}
          stroke="#0B0825"
          strokeOpacity={disabled ? 0.2 : 1}
          strokeWidth={1.2}
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </span>
  );
}
