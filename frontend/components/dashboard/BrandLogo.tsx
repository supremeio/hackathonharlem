import { assets } from "@/lib/assets";

/* === FIGMA DESIGN TOKENS === (node 11:1026)
   frame: 149 x 139, image cropped (overflow hidden) with the source scaled
   to 155.03% width / 161.15% height, offset left -30.2% / top -23.02%.
========================== */
export function BrandLogo() {
  return (
    <div className="relative h-[139px] w-[149px] shrink-0 overflow-hidden">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={assets.logo}
        alt="AI Deck Studio"
        className="pointer-events-none absolute left-[-30.2%] top-[-23.02%] h-[161.15%] w-[155.03%] max-w-none"
      />
    </div>
  );
}
