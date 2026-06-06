import { assets } from "@/lib/assets";
import type {
  FollowUpQuestion,
  InterviewQuestion,
  Model,
  Suggestion,
  Tier,
  User,
} from "@/types";

/**
 * Mock data standing in for backend responses. Keeping it isolated here means
 * the swap to a real API only touches `lib/api/index.ts` — these literals go away,
 * the function signatures stay identical.
 */

export const mockUser: User = {
  id: "usr_maverx",
  name: "Maverx",
  email: "marverx@hackathon.ai",
  avatarUrl: assets.profile,
  tier: "Tier 1",
};

export const mockSuggestions: Suggestion[] = [
  { id: "sug_1", text: "Onboard new hires on our tools and workflow" },
  { id: "sug_2", text: "Train managers on giving effective feedback" },
  { id: "sug_3", text: "Upskill the team on data storytelling" },
];

export const mockModels: Model[] = [
  { id: "claude-sonnet-4-6", name: "Claude Sonnet 4.6", iconUrl: assets.iconClaude },
];

export const mockTiers: Tier[] = [
  { id: "tier-1", label: "Tier 1", available: true },
  { id: "tier-2", label: "Tier 2 (CLI only)", available: false },
  { id: "tier-3", label: "Tier 3 (Coming soon)", available: false },
];

/** The fixed set of top-level interview questions. */
export const mockQuestions: InterviewQuestion[] = [
  {
    id: "q_topic",
    text: "What is the topic or skill to be trained?",
    placeholder: "What are you training today",
  },
  {
    id: "q_audience",
    text: "Who is the target audience?",
    placeholder: "Describe your audience",
  },
  {
    id: "q_level",
    text: "What is the knowledge level of participants?",
    placeholder: "e.g. Beginners, Intermediate, Advanced",
  },
  {
    id: "q_duration",
    text: "How long is the training?",
    placeholder: "e.g. 2 hours, half a day",
  },
  {
    id: "q_objective",
    text: "What is the primary learning objective?",
    placeholder: "By the end, participants will be able to build / explain / apply…",
  },
];

/**
 * Mock AI follow-up logic. Keyed by top-level question id; in production this is
 * a model call that decides whether a clarifying sub-question is warranted.
 */
export const mockFollowUps: Record<string, FollowUpQuestion> = {
  q_topic: {
    id: "q_topic_type",
    text: "What type of finance",
    placeholder: "e.g. Banking, Investing, Personal finance",
  },
};
