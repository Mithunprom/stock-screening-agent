import { CreditCard, ShieldCheck, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getCurrentSession } from "@/lib/server/auth";
import { getDashboardPayload, getUserPreferences } from "@/lib/server/research-store";

export default async function AccountPage() {
  const session = await getCurrentSession();
  const [dashboard, preferences] = await Promise.all([getDashboardPayload(), getUserPreferences()]);
  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs uppercase tracking-[0.24em] text-primary/80">Account</p>
        <h1 className="mt-2 font-display text-4xl font-semibold">Subscription and account scaffolding</h1>
      </div>
      <div className="grid gap-6 xl:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Profile</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="rounded-2xl border border-border/60 p-4">
              <p className="text-muted-foreground">Signed in as</p>
              <p className="mt-2 font-semibold">{session?.email ?? "demo@stockagent.local"}</p>
            </div>
            <div className="rounded-2xl border border-border/60 p-4">
              <p className="text-muted-foreground">Risk tolerance</p>
              <p className="mt-2 font-semibold">{preferences.riskTolerance}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Plan</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex items-center gap-3 rounded-2xl border border-border/60 p-4">
              <Sparkles className="size-5 text-primary" />
              <div>
                <p className="font-semibold">Research Pro</p>
                <p className="text-muted-foreground">Watchlists, signal detail pages, email alerts, and paper portfolio.</p>
              </div>
            </div>
            <div className="rounded-2xl border border-border/60 p-4">
              <p className="text-muted-foreground">Tracked tickers</p>
              <p className="mt-2 font-semibold">{preferences.watchlist.length}</p>
            </div>
            <Button variant="outline" className="w-full">
              Connect Stripe billing later
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Usage</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex items-center gap-3 rounded-2xl border border-border/60 p-4">
              <ShieldCheck className="size-5 text-primary" />
              <div>
                <p className="font-semibold">Hourly digests</p>
                <p className="text-muted-foreground">Active during market hours with watchlist-based filtering.</p>
              </div>
            </div>
            <div className="flex items-center gap-3 rounded-2xl border border-border/60 p-4">
              <CreditCard className="size-5 text-primary" />
              <div>
                <p className="font-semibold">API / model freshness</p>
                <p className="text-muted-foreground">Last factor refresh: {new Date(dashboard.model_freshness.factor).toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
