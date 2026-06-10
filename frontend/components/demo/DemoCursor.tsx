"use client";

import { useReducedMotion } from "@/lib/demo/useReducedMotion";

/* A fake, smoothly-animated cursor for the auto-playing demo. Glides between
   targets with eased CSS transitions and pulses a ripple on "click". Honors
   prefers-reduced-motion by snapping instead of gliding. */
export function DemoCursor({ x, y, down }: { x: number; y: number; down: boolean }) {
  const reduced = useReducedMotion();
  return (
    <div
      aria-hidden
      className="pointer-events-none fixed left-0 top-0 z-[100]"
      style={{
        transform: `translate(${x}px, ${y}px)`,
        transition: reduced ? "none" : "transform 250ms cubic-bezier(0.65, 0, 0.35, 1)",
        willChange: "transform",
      }}
    >
      {/* click ripple */}
      <span
        className="absolute left-0 top-0 -translate-x-1/2 -translate-y-1/2 rounded-full"
        style={{
          width: 34,
          height: 34,
          background: "rgba(84, 0, 173, 0.28)",
          opacity: down ? 1 : 0,
          transform: `translate(-50%, -50%) scale(${down ? 1.15 : 0.2})`,
          transition: "transform 280ms ease-out, opacity 280ms ease-out",
        }}
      />
      {/* pointer */}
      <svg
        width="26"
        height="26"
        viewBox="0 0 24 24"
        fill="none"
        style={{
          position: "absolute",
          left: -2,
          top: -2,
          transform: down ? "scale(0.82)" : "scale(1)",
          transformOrigin: "top left",
          transition: "transform 130ms ease",
          filter: "drop-shadow(0 2px 4px rgba(26, 19, 54, 0.35))",
        }}
      >
        <path
          d="M5 2.5 L5 19 L9.2 14.8 L12 20.8 L14.7 19.6 L11.9 13.7 L18 13.7 Z"
          fill="#1A1336"
          stroke="#FFFFFF"
          strokeWidth="1.4"
          strokeLinejoin="round"
        />
      </svg>
    </div>
  );
}
