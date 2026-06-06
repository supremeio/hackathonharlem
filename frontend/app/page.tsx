import { DashboardView } from "@/components/dashboard/DashboardView";
import {
  getCurrentUser,
  getDeckGroups,
  getModels,
  getSuggestions,
  getTiers,
} from "@/lib/api";

/**
 * Dashboard route. Runs on the server and loads all data through the
 * data-access layer before handing it to the interactive client shell.
 * When the backend is live, only `lib/api` changes — this file stays as-is.
 */
export default async function DashboardPage() {
  const [user, deckGroups, suggestions, models, tiers] = await Promise.all([
    getCurrentUser(),
    getDeckGroups(),
    getSuggestions(),
    getModels(),
    getTiers(),
  ]);

  return (
    <DashboardView
      user={user}
      deckGroups={deckGroups}
      suggestions={suggestions}
      models={models}
      tiers={tiers}
    />
  );
}
