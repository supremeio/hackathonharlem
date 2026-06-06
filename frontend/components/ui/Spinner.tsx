/* === FIGMA === 8-spoke loader (node 332:6628), stroke #DDD2A3 (panel) / #257498 (inline).
   The svg is centred by the flex parent and spins around its own centre — keep the
   rotation and the centring on separate elements so they don't clobber each other. */
export function Spinner({
  size = 20,
  color = "#257498",
  className = "",
}: {
  size?: number;
  color?: string;
  className?: string;
}) {
  // Figma renders the 16px glyph at 12.5% inset inside a 20px box → 15px glyph.
  const glyph = (size / 20) * 15;
  return (
    <span
      className={`flex shrink-0 items-center justify-center ${className}`}
      style={{ width: size, height: size }}
      aria-hidden
    >
      <svg
        className="origin-center animate-spin [animation-duration:1s]"
        width={glyph}
        height={glyph}
        viewBox="0 0 16 16"
        fill="none"
      >
        <path
          d="M8 3V0.5M11.5417 4.45833L13.3333 2.66667M13 8H15.5M11.5417 11.5417L13.3333 13.3333M8 13V15.5M4.45833 11.5417L2.66667 13.3333M3 8H0.5M4.45833 4.45833L2.66667 2.66667"
          stroke={color}
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </span>
  );
}
