"use client";

import type { DeckGroup, User } from "@/types";
import { UserProfile } from "./UserProfile";
import { CreateButton } from "./CreateButton";
import { DeckHistory } from "./DeckHistory";

/* === FIGMA DESIGN TOKENS === (node 11:1690 "Sidebar")
   outer: bg #f6f6f6, w-331, full height, p-16
   card:  bg white, rounded-24, p-24, flex col justify-between, fills height
   stack: Profile Container gap-24 → { UserProfile, Tasks gap-40 → { Create, History } }
========================== */
export function Sidebar({
  user,
  deckGroups,
  onCreate,
  onSelectDeck,
}: {
  user: User;
  deckGroups: DeckGroup[];
  onCreate?: () => void;
  onSelectDeck?: (deckId: string) => void;
}) {
  return (
    <aside className="flex h-full w-[331px] shrink-0 flex-col items-start justify-center bg-canvas p-[16px]">
      <div className="flex min-h-px w-full flex-1 flex-col items-start rounded-card bg-white p-[24px]">
        <div className="flex w-full flex-col items-start gap-[24px]">
          <UserProfile user={user} />
          <div className="flex w-full flex-col items-start gap-[40px]">
            <CreateButton onClick={onCreate} />
            <DeckHistory groups={deckGroups} onSelect={onSelectDeck} />
          </div>
        </div>
      </div>
    </aside>
  );
}
