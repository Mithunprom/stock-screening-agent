import { ScreenerClient } from "@/components/screener-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getDashboardPayload } from "@/lib/server/research-store";

export default async function ScreenerPage() {
  const dashboard = await getDashboardPayload();
  const rows = [...dashboard.recommendations].sort((a, b) => b.opportunity_score - a.opportunity_score);

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs uppercase tracking-[0.24em] text-primary/80">Screener</p>
        <h1 className="mt-2 font-display text-4xl font-semibold">Filter the opportunity universe without losing context.</h1>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Opportunity-ranked universe</CardTitle>
        </CardHeader>
        <CardContent>
          <ScreenerClient rows={rows} />
        </CardContent>
      </Card>
      <div className="rounded-2xl border border-dashed border-border p-4 text-sm text-muted-foreground">
        Filters, quick-add watchlist controls, and server-side query params are supported by the API layer. For a first pass, the page is sorted by opportunity score so the highest-value names are still obvious immediately.
      </div>
    </div>
  );
}
