import type { Metadata } from "next";
import { Figtree, Space_Grotesk, Raleway } from "next/font/google";
import "./globals.css";

const figtree = Figtree({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-figtree",
  display: "swap",
});

// Maverx house style — used in the generated-deck preview.
const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  weight: ["500", "600", "700"],
  variable: "--font-grotesk",
  display: "swap",
});

const raleway = Raleway({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-raleway",
  display: "swap",
});

export const metadata: Metadata = {
  title: "AI Deck Studio",
  description: "Create decks, lessons, and quizzes with AI.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${figtree.variable} ${spaceGrotesk.variable} ${raleway.variable}`}
    >
      <body className="font-sans">{children}</body>
    </html>
  );
}
