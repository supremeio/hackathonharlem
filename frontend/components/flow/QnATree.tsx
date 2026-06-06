"use client";

import { useEffect, useRef, useState } from "react";
import { assets } from "@/lib/assets";
import type { AnswerNode } from "@/types";

/* === FIGMA DESIGN TOKENS === (node 7:866 "Question Group")
   group:    flex col gap-40, w-463
   row:      flex gap-16 items-start
   bullet:   4×20 dot (#0b0825); first = bullet.svg, rest = checkbox.svg (masks thread)
   thread:   gradient line #403F4E→transparent (node 7:807) — drawn progressively
             from the first bullet down to the most recently answered one
   question: Figtree Medium 14px/20px rgba(11,8,37,0.5)
   answer:   Figtree Medium 14px/20px #0b0825
   sub-row:  gap-8; ↳ arrow (#8892a7, 20px, rotated 180) + muted Q / dark A (w-403)
========================== */

function QA({ question, answer }: { question: string; answer: string }) {
  return (
    <div className="flex w-full flex-col gap-[4px] text-[15px] font-medium leading-[20px] [word-break:break-word]">
      <p className="w-full text-[rgba(11,8,37,0.5)]">{question}</p>
      <p className="w-full text-ink">{answer}</p>
    </div>
  );
}

export function QnATree({ nodes }: { nodes: AnswerNode[] }) {
  const containerRef = useRef<HTMLDivElement>(null);
  // The progress line runs from the first bullet's centre to the last one's.
  const [line, setLine] = useState({ top: 0, height: 0 });

  useEffect(() => {
    const measure = () => {
      const container = containerRef.current;
      if (!container) return;
      const bullets = Array.from(
        container.querySelectorAll<HTMLElement>("[data-bullet]"),
      );
      if (bullets.length < 2) {
        setLine({ top: 0, height: 0 });
        return;
      }
      // Layout position relative to the container, ignoring the rise transform
      // so the line animates to each bullet's *settled* spot.
      const centerY = (el: HTMLElement) => {
        let y = el.offsetHeight / 2;
        let node: HTMLElement | null = el;
        while (node && node !== container) {
          y += node.offsetTop;
          node = node.offsetParent as HTMLElement | null;
        }
        return y;
      };
      const first = centerY(bullets[0]);
      const last = centerY(bullets[bullets.length - 1]);
      const next = { top: first, height: Math.max(0, last - first) };
      setLine((prev) =>
        prev.top === next.top && prev.height === next.height ? prev : next,
      );
    };
    measure();
    window.addEventListener("resize", measure);
    return () => window.removeEventListener("resize", measure);
  }, [nodes]);

  return (
    <div ref={containerRef} className="relative flex w-full flex-col gap-[40px]">
      {/* Progress thread — height animates as each new answer extends it down */}
      <div
        className="pointer-events-none absolute left-[1.5px] w-px rounded-full bg-gradient-to-b from-[#403F4E] to-transparent transition-[height] duration-[600ms] ease-out"
        style={{ top: line.top, height: line.height }}
        aria-hidden
      />

      {nodes.map((node, i) => (
        <div key={node.questionId} className="relative flex w-full animate-rise items-start gap-[16px]">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            data-bullet
            src={i === 0 ? assets.bullet : assets.checkbox}
            alt=""
            className="relative z-10 h-[20px] w-[4px] shrink-0"
            aria-hidden
          />
          <div className="flex min-w-0 flex-1 flex-col gap-[16px]">
            <QA question={node.question} answer={node.answer} />
            {(node.followUps ?? []).map((fu, fi) => (
              <div key={fi} className="flex w-full animate-rise items-start gap-[8px]">
                <span className="flex shrink-0 rotate-180 items-center justify-center">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={assets.iconSubArrow}
                    alt=""
                    className="block size-[20px] max-w-none"
                    aria-hidden
                  />
                </span>
                <div className="min-w-0 flex-1">
                  <QA question={fu.question} answer={fu.answer} />
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
