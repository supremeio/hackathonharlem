"use client";

import { useLayoutEffect, useRef, useState } from "react";

/**
 * Smoothly animates its own height to fit its content. The content is pinned to
 * the bottom, so the box grows/shrinks upward — ideal for a bottom-anchored input
 * card that gets taller when a follow-up banner or a longer question appears.
 */
export function AnimateHeight({
  children,
  className = "",
  duration = 380,
}: {
  children: React.ReactNode;
  className?: string;
  duration?: number;
}) {
  const inner = useRef<HTMLDivElement>(null);
  const [height, setHeight] = useState<number>();
  const [animate, setAnimate] = useState(false);

  useLayoutEffect(() => {
    const el = inner.current;
    if (!el) return;
    const measure = () => setHeight(el.offsetHeight);
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(el);
    // Enable the transition only after the first measurement so the initial
    // render snaps to size instead of animating from zero.
    const raf = requestAnimationFrame(() => setAnimate(true));
    return () => {
      ro.disconnect();
      cancelAnimationFrame(raf);
    };
  }, []);

  return (
    <div
      className={`relative overflow-hidden ${className}`}
      style={{
        height,
        transition: animate
          ? `height ${duration}ms cubic-bezier(0.22, 0.61, 0.36, 1)`
          : undefined,
      }}
    >
      <div ref={inner} className="absolute inset-x-0 bottom-0">
        {children}
      </div>
    </div>
  );
}
