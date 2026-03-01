import { NewsFeed } from "@/components/news-feed";
import { WatchlistClient } from "@/components/watchlist-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getDashboardPayload, getUserPreferences } from "@/lib/server/research-store";

export default async function WatchlistPage() {
  const [dashboard, preferences] = await Promise.all([getDashboardPayload(), getUserPreferences()]);

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs uppercase tracking-[0.24em] text-primary/80">Watchlist</p>
        <h1 className="mt-2 font-display text-4xl font-semibold">Own the alert thresholds before the hourly digest does.</h1>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Alert controls</CardTitle>
        </CardHeader>
        <CardContent>
          <WatchlistClient items={preferences.watchlist} />
        </CardContent>
      </Card>
      <NewsFeed items={dashboard.news.filter((item) => preferences.watchlist.some((watch) => watch.ticker === item.ticker))} title="Tracked ticker catalyst feed" />
    </div>
  );
}
