import type { Config } from "tailwindcss";

/**
 * Design tokens extracted from the Figma source (node 3:2).
 * Centralising them here keeps every component on a single source of truth
 * and makes future theme/brand changes a one-file edit.
 */
const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: "#F9FBFB",
        surface: "#EEF2F5",
        ink: "#0b0825",
        muted: "#8892a7",
        "welcome-bg": "#f5f0ff",
        "welcome-ink": "#25144a",
        "welcome-border": "#417499",
        // Single source of truth for all borders/strokes.
        stroke: "#E2E8F0",
        "input-focus": "#25144A",
        // Maverx house style (generated-deck preview) — from maverx/config.py
        brand: {
          indigo: "#0D006A",
          purple: "#5400AD",
          orange: "#F79421",
          coral: "#EF4453",
          magenta: "#D3116E",
          gold: "#BF9000",
          black: "#3A3838",
          lavender: "#F1EDF9",
          tint: "#E9ECF2",
        },
      },
      fontFamily: {
        sans: ["var(--font-figtree)", "system-ui", "sans-serif"],
        grotesk: ["var(--font-grotesk)", "system-ui", "sans-serif"],
      },
      borderRadius: {
        card: "24px",
        input: "23px",
        pill: "40px",
        chip: "400px",
      },
    },
  },
  plugins: [],
};

export default config;
