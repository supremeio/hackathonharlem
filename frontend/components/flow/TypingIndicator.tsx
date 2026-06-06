/* Assistant "typing" bubble — shown while the AI reads the user's first message
   and extracts any answers it already contains. White pill (mirrors ChatBubble)
   with a label and three bouncing dots. */
export function TypingIndicator({
  label = "Reading your message",
}: {
  label?: string;
}) {
  return (
    <div className="flex items-center gap-[10px] rounded-pill bg-white p-[16px]">
      <span className="whitespace-nowrap text-[15px] font-medium leading-normal text-muted [word-break:break-word]">
        {label}
      </span>
      <span className="flex items-center gap-[4px]" aria-hidden>
        <span className="size-[6px] animate-bounce rounded-full bg-muted [animation-delay:-0.32s]" />
        <span className="size-[6px] animate-bounce rounded-full bg-muted [animation-delay:-0.16s]" />
        <span className="size-[6px] animate-bounce rounded-full bg-muted" />
      </span>
    </div>
  );
}
