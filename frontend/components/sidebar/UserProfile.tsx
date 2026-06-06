import type { User } from "@/types";

/* === FIGMA DESIGN TOKENS === (node 11:1693 "User Profile")
   container: bg white, px-16 py-12, flex col items-center, w-full
   avatar: 32x32 ellipse
   gap avatar→text: 8px
   name:  Figtree SemiBold 16px #0b0825
   email: Figtree Regular  12px #0b0825
========================== */
export function UserProfile({ user }: { user: User }) {
  return (
    <div className="flex w-full flex-col items-center bg-white px-[16px] py-[12px]">
      <div className="flex w-full items-center gap-[8px]">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={user.avatarUrl}
          alt={user.name}
          width={32}
          height={32}
          className="size-[32px] shrink-0 rounded-full object-cover"
        />
        <div className="flex min-w-px flex-1 items-center gap-[8px]">
          <div className="flex w-[185px] flex-col items-start whitespace-nowrap text-ink [word-break:break-word]">
            <p className="text-[16px] font-semibold leading-normal">{user.name}</p>
            <p className="text-[12px] font-normal leading-normal">{user.email}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
