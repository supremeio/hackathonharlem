/* === FIGMA DESIGN TOKENS === (node 11:1091 "Header")
   wrapper: w-680, flex gap-4
   badge:   bg #f5f0ff, border 0.2px solid #417499, px-16 py-8 (no radius)
   title:   Figtree SemiBold 32px #25144a
   subtitle:Figtree SemiBold 32px #8892a7
========================== */
export function WelcomeHeader({ name }: { name: string }) {
  return (
    <div className="flex w-[680px] items-start gap-[4px]">
      <div className="flex min-w-px flex-1 flex-col items-start gap-[4px]">
        <div className="flex items-center justify-center border-[0.4px] border-solid border-[#25144A] bg-welcome-bg px-[16px] py-[8px]">
          <p className="whitespace-nowrap text-[32px] font-semibold leading-normal text-welcome-ink [word-break:break-word]">
            Welcome, {name} 👋
          </p>
        </div>
        <p className="min-w-full text-[32px] font-semibold leading-normal text-muted [word-break:break-word]">
          Let&rsquo;s create some deck today
        </p>
      </div>
    </div>
  );
}
