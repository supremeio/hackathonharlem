"use client";

import { useState } from "react";
import { assets } from "@/lib/assets";
import { Icon } from "@/components/ui/Icon";
import { Chevron } from "@/components/ui/Chevron";
import type { DeckResult, PreviewSlide } from "@/types";

/* Renders the generated Training plan as styled slide cards that mirror the
   Maverx deck (maverx/deck.py + config.py house style): Space Grotesk titles,
   Raleway body, the indigo/orange/coral palette, callouts, cards and number rows.
   Floats over the dimmed overlay. */

const SEQUENCE = ["#5400AD", "#D3116E", "#BF9000", "#F79421", "#3A3838"]; // brand circle order

/* ── small building blocks ─────────────────────────────────────────────── */

function Title({ text, light = false }: { text: string; light?: boolean }) {
  return (
    <h3 className={`font-grotesk text-[24px] font-semibold leading-[28px] [word-break:break-word] ${light ? "text-white" : "text-brand-indigo"}`}>
      {text}
    </h3>
  );
}

function Bullets({ items }: { items: string[] }) {
  return (
    <ul className="flex flex-col gap-[8px] font-grotesk">
      {items.map((item, i) => {
        const [head, ...rest] = item.split(" — ");
        const sub = rest.join(" — ");
        return (
          <li key={i} className="[word-break:break-word]">
            <span className="text-[15px] font-semibold text-brand-indigo">{head}</span>
            {sub && (
              <span className="mt-[2px] flex gap-[6px] text-[13px] text-brand-black">
                <span className="font-bold text-brand-orange">•</span>
                <span>{sub}</span>
              </span>
            )}
          </li>
        );
      })}
    </ul>
  );
}

function Callout({ label, body, fill }: { label: string; body: string; fill: string }) {
  return (
    <div className="rounded-[10px] px-[16px] py-[12px]" style={{ background: fill }}>
      <p className="font-grotesk text-[11px] font-bold uppercase tracking-wide text-white">{label}</p>
      <p className="mt-[4px] font-grotesk text-[14px] leading-[19px] text-white [word-break:break-word]">{body}</p>
    </div>
  );
}

function MiniCard({ head, color, lines }: { head: string; color: string; lines: string[] }) {
  return (
    <div className="flex flex-col rounded-[10px] border border-solid border-brand-lavender bg-white p-[12px]">
      <div className="flex items-center gap-[8px]">
        <span className="size-[10px] shrink-0 rounded-full" style={{ background: color }} />
        <span className="font-grotesk text-[13px] font-bold" style={{ color }}>{head}</span>
      </div>
      <ul className="mt-[6px] flex flex-col gap-[3px] font-grotesk text-[12px] leading-[16px] text-brand-black">
        {lines.map((l, i) => (
          <li key={i} className="[word-break:break-word]">{l}</li>
        ))}
      </ul>
    </div>
  );
}

/* ── per-kind slide renderers ──────────────────────────────────────────── */

function DarkSlide({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-full w-full flex-col justify-center gap-[12px] rounded-[8px] bg-gradient-to-br from-brand-indigo to-brand-purple px-[40px] py-[36px]">
      {children}
    </div>
  );
}

function LightSlide({ block, children }: { block?: string; children: React.ReactNode }) {
  return (
    <div className="flex h-full w-full flex-col gap-[14px] rounded-[8px] border border-solid border-stroke bg-white px-[28px] py-[24px]">
      {block && (
        <span className="font-grotesk text-[11px] font-bold uppercase tracking-wide text-brand-purple">{block}</span>
      )}
      {children}
    </div>
  );
}

function SlideStage({ slide: s }: { slide: PreviewSlide }) {
  const d = s as any;
  switch (s.kind) {
    case "cover":
      return (
        <DarkSlide>
          <h2 className="font-grotesk text-[34px] font-bold leading-[40px] text-white [word-break:break-word]">{d.title}</h2>
          {d.subtitle && <p className="font-grotesk text-[20px] font-semibold text-brand-orange [word-break:break-word]">{d.subtitle}</p>}
        </DarkSlide>
      );
    case "section":
      return (
        <DarkSlide>
          <Title text={d.title} light />
          {d.subtitle && <p className="font-grotesk text-[16px] font-semibold text-brand-orange">{d.subtitle}</p>}
        </DarkSlide>
      );
    case "closing":
      return (
        <DarkSlide>
          <Title text={d.title} light />
          <ul className="mt-[6px] flex flex-col gap-[8px] font-grotesk">
            {(d.reflection ?? []).map((q: string, i: number) => (
              <li key={i} className="flex gap-[8px] text-[16px] font-semibold text-white [word-break:break-word]">
                <span className="text-brand-orange">•</span>
                <span>{q}</span>
              </li>
            ))}
          </ul>
        </DarkSlide>
      );
    case "about":
      return (
        <LightSlide>
          <Title text={d.title} />
          <div className="grid grid-cols-2 gap-[10px] overflow-y-auto">
            <MiniCard head="Learning objectives" color="#5400AD" lines={d.objectives ?? []} />
            <MiniCard head="Learning outcomes" color="#F79421" lines={d.outcomes ?? []} />
            <MiniCard head="Target group" color="#D3116E" lines={[d.target_group].filter(Boolean)} />
            <MiniCard head="Good to know" color="#0D006A" lines={d.good_to_know ?? []} />
          </div>
        </LightSlide>
      );
    case "timetable":
      return (
        <LightSlide>
          <Title text={d.title} />
          <div className="overflow-y-auto rounded-[8px] border border-solid border-brand-lavender">
            <table className="w-full border-collapse font-grotesk text-[13px]">
              <thead>
                <tr className="bg-brand-indigo text-white">
                  <th className="px-[12px] py-[7px] text-left font-semibold">Segment</th>
                  <th className="px-[12px] py-[7px] text-left font-semibold">Time</th>
                  <th className="px-[12px] py-[7px] text-left font-semibold">What happens</th>
                </tr>
              </thead>
              <tbody>
                {(d.rows ?? []).map((r: any, i: number) => (
                  <tr key={i} className={i % 2 ? "bg-brand-lavender" : "bg-white"}>
                    <td className="px-[12px] py-[6px] font-semibold text-brand-black">{r.segment}</td>
                    <td className="px-[12px] py-[6px] text-brand-black">{r.minutes} min</td>
                    <td className="px-[12px] py-[6px] text-brand-black">{r.activity}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </LightSlide>
      );
    case "phases":
      return (
        <LightSlide>
          <Title text={d.title} />
          <div className="flex flex-1 items-center justify-center gap-[6px]">
            {(d.phases ?? []).map((p: string, i: number) => (
              <div key={i} className="flex items-center gap-[6px]">
                <div className="flex flex-col items-center gap-[8px]" style={{ maxWidth: 110 }}>
                  <span
                    className="flex size-[46px] items-center justify-center rounded-full font-grotesk text-[18px] font-bold text-white"
                    style={{ background: SEQUENCE[i % SEQUENCE.length] }}
                  >
                    {i + 1}
                  </span>
                  <span className="text-center font-grotesk text-[12px] font-semibold text-brand-indigo [word-break:break-word]">{p}</span>
                </div>
                {i < (d.phases ?? []).length - 1 && <span className="text-brand-indigo">→</span>}
              </div>
            ))}
          </div>
        </LightSlide>
      );
    case "agenda":
    case "kickoff":
    case "takeaways":
    case "whats_next":
      return (
        <LightSlide>
          <Title text={d.title} />
          <div className="overflow-y-auto">
            <Bullets items={d.items ?? d.goals ?? []} />
          </div>
        </LightSlide>
      );
    case "theory":
      return (
        <LightSlide block={d.block}>
          <Title text={d.title} />
          {d.definition && <Callout label="Definition" body={d.definition} fill="#5400AD" />}
          <div className="overflow-y-auto">
            <Bullets items={d.points ?? []} />
          </div>
          {d.statement && <p className="font-grotesk text-[16px] font-bold text-brand-indigo [word-break:break-word]">{d.statement}</p>}
        </LightSlide>
      );
    case "example":
      return (
        <LightSlide block={d.block}>
          <Title text={d.title} />
          {d.scenario && <Callout label="Example" body={d.scenario} fill="#0D006A" />}
          <div className="overflow-y-auto">
            <Bullets items={d.points ?? []} />
          </div>
        </LightSlide>
      );
    case "exercise":
      return (
        <LightSlide block={d.block}>
          <Title text={d.title} />
          <p className="font-grotesk text-[12px] font-bold uppercase tracking-wide text-brand-magenta">
            {String(d.fmt ?? "group")} · {d.duration_min ?? 15} min
          </p>
          <div className="overflow-y-auto">
            <Bullets items={(d.steps ?? []).map((st: string, i: number) => `${i + 1}. ${st}`)} />
            {(d.debrief ?? []).length > 0 && (
              <>
                <p className="mt-[10px] font-grotesk text-[14px] font-bold text-brand-indigo">Debrief</p>
                <ul className="mt-[4px] flex flex-col gap-[4px] font-grotesk text-[13px] text-brand-black">
                  {(d.debrief ?? []).map((q: string, i: number) => (
                    <li key={i} className="flex gap-[6px] [word-break:break-word]">
                      <span className="text-brand-orange">•</span>
                      <span>{q}</span>
                    </li>
                  ))}
                </ul>
              </>
            )}
          </div>
        </LightSlide>
      );
    default:
      return (
        <LightSlide>
          <Title text={d.title ?? ""} />
        </LightSlide>
      );
  }
}

/* ── panel ─────────────────────────────────────────────────────────────── */

export function ResultPanel({
  result,
  onClose,
}: {
  result: DeckResult;
  onClose?: () => void;
}) {
  const [index, setIndex] = useState(0);
  const slides = result.slides ?? [];
  const slide = slides[Math.min(index, slides.length - 1)];
  const total = slides.length;

  function open(url: string) {
    if (url) window.open(url, "_blank", "noopener,noreferrer");
  }

  return (
    <aside className="flex h-full w-[763px] flex-col items-start justify-center p-[16px]">
      <div className="flex min-h-px w-full flex-1 flex-col items-center rounded-card bg-white p-[24px]">
        <div className="flex w-full flex-col items-start gap-[8px]">
          {/* Meta pills + close */}
          <div className="flex w-full items-center justify-between">
            <div className="flex items-start gap-[8px]">
              <div className="flex items-center gap-[4px] rounded-pill bg-welcome-bg px-[16px] py-[6px]">
                <Icon src={assets.iconSlide} size={16} />
                <span className="whitespace-nowrap text-[15px] font-medium leading-normal text-black [word-break:break-word]">
                  {result.pageCount} pages
                </span>
              </div>
              <div className="flex items-center gap-[4px] rounded-pill bg-welcome-bg px-[16px] py-[6px]">
                <Icon src={assets.iconTime} size={16} />
                <span className="whitespace-nowrap text-[15px] font-medium leading-normal text-black [word-break:break-word]">
                  {result.durationLabel}
                </span>
              </div>
            </div>
            <button
              type="button"
              onClick={onClose}
              aria-label="Close preview"
              className="shrink-0 transition-opacity hover:opacity-70"
            >
              <Icon src={assets.iconClose} size={24} />
            </button>
          </div>

          {/* Slide preview */}
          {slide ? (
            <div className="group relative h-[400px] w-full">
              <SlideStage slide={slide} />
              {total > 1 && (
                <>
                  <button
                    type="button"
                    onClick={() => setIndex((i) => Math.max(0, i - 1))}
                    disabled={index === 0}
                    aria-label="Previous slide"
                    className="absolute left-[12px] top-1/2 flex size-[36px] -translate-y-1/2 items-center justify-center rounded-full border border-solid border-stroke bg-white/95 opacity-0 transition-opacity group-hover:opacity-100 disabled:opacity-0"
                  >
                    <Chevron direction="left" />
                  </button>
                  <button
                    type="button"
                    onClick={() => setIndex((i) => Math.min(total - 1, i + 1))}
                    disabled={index === total - 1}
                    aria-label="Next slide"
                    className="absolute right-[12px] top-1/2 flex size-[36px] -translate-y-1/2 items-center justify-center rounded-full border border-solid border-stroke bg-white/95 opacity-0 transition-opacity group-hover:opacity-100 disabled:opacity-0"
                  >
                    <Chevron direction="right" />
                  </button>
                </>
              )}
            </div>
          ) : (
            <div className="h-[400px] w-full rounded-[8px] bg-[#d9d9d9]" />
          )}

          {/* Downloads + counter */}
          <div className="flex w-full items-center justify-between pt-[2px]">
            <div className="flex items-center gap-[16px]">
              <button
                type="button"
                onClick={() => open(result.downloadUrl ?? "")}
                disabled={!result.downloadUrl}
                className="flex items-center gap-[4px] transition-opacity hover:opacity-70 disabled:opacity-40"
              >
                <Icon src={assets.iconDownload} size={20} />
                <span className="whitespace-nowrap text-[15px] font-medium leading-normal text-black [word-break:break-word]">
                  Download slides
                </span>
              </button>
              {result.downloads?.prebite && (
                <button type="button" onClick={() => open(result.downloads.prebite)} className="text-[13px] font-medium text-muted transition-colors hover:text-ink">
                  Pre-bite
                </button>
              )}
              {result.downloads?.postbite && (
                <button type="button" onClick={() => open(result.downloads.postbite)} className="text-[13px] font-medium text-muted transition-colors hover:text-ink">
                  Post-bite
                </button>
              )}
            </div>
            {total > 0 && (
              <span className="text-[13px] font-medium text-muted">
                Slide {index + 1} of {total}
              </span>
            )}
          </div>
        </div>
      </div>
    </aside>
  );
}
