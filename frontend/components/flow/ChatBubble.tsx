/* === FIGMA DESIGN TOKENS === (node 11:1256 "User Input Container")
   bg white, p-16, rounded-40; text Figtree Medium 14px #0b0825 */
export function ChatBubble({ text }: { text: string }) {
  return (
    <div className="flex items-center justify-center rounded-pill bg-white p-[16px]">
      <p className="whitespace-nowrap text-[15px] font-medium leading-normal text-ink [word-break:break-word]">
        {text}
      </p>
    </div>
  );
}
