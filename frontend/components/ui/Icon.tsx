/**
 * Renders a Figma-exported SVG/PNG icon at an exact pixel box.
 * Use for icons that fill their frame 1:1. Icons that Figma insets within their
 * frame (create / settings / arrow-up) keep their bespoke wrappers inline.
 */
export function Icon({
  src,
  size,
  className = "",
}: {
  src: string;
  size: number;
  className?: string;
}) {
  return (
    <span
      className={`relative block shrink-0 ${className}`}
      style={{ width: size, height: size }}
      aria-hidden
    >
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={src} alt="" className="absolute inset-0 block size-full max-w-none" />
    </span>
  );
}
