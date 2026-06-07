import { DemoShowcase } from "@/components/demo/DemoShowcase";

export const metadata = {
  title: "AI Deck Studio — Demo",
  description: "An auto-playing walkthrough of the Maverx AI Training Builder.",
};

/**
 * Self-contained, auto-playing showcase of the full product flow. No backend —
 * everything is scripted on canned data, so this page works as a static deploy.
 */
export default function DemoPage() {
  return <DemoShowcase />;
}
