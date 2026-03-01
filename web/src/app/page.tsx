import { Activity, Gauge, ShieldCheck, Zap } from "lucide-react";

import { DataStatusCard } from "@/components/data-status";
import { LiveClock } from "@/components/live-clock";
import { LiveSignalStrip } from "@/components/live-signal-strip";
import { MetricCard } from "@/components/metric-card";
import { NewsFeed } from "@/components/news-feed";
import { OnboardingWizard } from "@/components/onboarding-wizard";
import { TopOpportunityCard } from "@/components/top-opportunity-card";
import { VolatilityTable } from "@/components/volatility-table";
import { ActionBadge, RiskBadge } from "@/components/status-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getDashboardPayload, getTopVolatile, getUserPreferences } from "@/lib/server/research-store";
import { formatCurrency, formatPercent } from "@/lib/utils";

export default async function DashboardPage() {
  const [dashboard, topVolatile, preferences] = await Promise.all([getDashboardPayload(), getTopVolatile(20), getUserPreferences()]);
  const topOpportunities = dashboard.watchlist.slice(0, 5);

  return (
    <div className="space-y-8">
      <OnboardingWizard preferences={preferences} recommendedTickers={dashboard.watchlist.map((item) => item.ticker)} />
      <section className="grid gap-6 xl:grid-cols-[1.6fr_0.8fr]">
        <Card className="overflow-hidden border-none bg-hero-glow shadow-soft">
          <CardContent className="p-8">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
              <div className="max-w-2xl">
                <p className="text-xs uppercase tracking-[0.32em] text-primary/80">Today’s Top Opportunities</p>
                <h1 className="mt-4 font-display text-4xl font-semibold tracking-tight">A faster way to decide whether a stock is worth your attention, and why.</h1>
                <p className="mt-4 max-w-xl text-base text-muted-foreground">
                  The dashboard prioritizes signal quality, catalyst intensity, invalidation levels, and paper-risk context so the first screen already answers what to look at.
                </p>
              </div>
              <div className="rounded-2xl bg-background/80 px-4 py-3 text-sm text-muted-foreground">
                <LiveClock updatedAt={dashboard.as_of} />
              </div>
            </div>
            <div className="mt-6">
              <LiveSignalStrip tickers={topOpportunities.map((item) => item.ticker)} />
            </div>
          </CardContent>
        </Card>
        <DataStatusCard updatedAt={dashboard.as_of} latencyMs={dashboard.data_status.latencyMs} feed={dashboard.data_status.feed} note={dashboard.data_status.note} level={dashboard.data_status.level} />
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Market regime" value={dashboard.market_context.risk_regime} hint={`SPY ${formatPercent(dashboard.market_context.spy_ret_1d)} | QQQ ${formatPercent(dashboard.market_context.qqq_ret_1d)}`} icon={<Gauge className="size-4 text-primary" />} />
        <MetricCard label="Paper equity" value={formatCurrency(dashboard.portfolio_state.equityCurve.at(-1)?.equity ?? 0)} hint={`Kill-switch ${dashboard.portfolio_state.kill_switch_active ? "active" : "inactive"}`} icon={<ShieldCheck className="size-4 text-primary" />} />
        <MetricCard label="Validation hit-rate" value={formatPercent(dashboard.backtest_summary.hit_rate)} hint={`IC ${dashboard.backtest_summary.ic.toFixed(2)} | IR ${dashboard.backtest_summary.ic_ir.toFixed(2)}`} icon={<Activity className="size-4 text-primary" />} />
        <MetricCard label="Tracked catalysts" value={String(dashboard.news.length)} hint="Major-news feed used in alerts and ticker detail pages." icon={<Zap className="size-4 text-primary" />} />
      </section>

      <section className="grid gap-4 xl:grid-cols-5">
        {topOpportunities.map((item) => (
          <TopOpportunityCard key={item.ticker} item={item} />
        ))}
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.35fr_0.65fr]">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Top 20 Volatile (5D)</CardTitle>
            <p className="text-sm text-muted-foreground">Sortable screener view with catalyst and confidence context.</p>
          </CardHeader>
          <CardContent>
            <VolatilityTable rows={topVolatile} />
          </CardContent>
        </Card>
        <NewsFeed items={dashboard.news} />
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>My Watchlist</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {dashboard.watchlist.slice(0, 5).map((item) => (
              <div key={item.ticker} className="flex items-center justify-between rounded-2xl border border-border/60 p-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold">{item.ticker}</span>
                    <ActionBadge value={item.action} />
                    <RiskBadge value={item.risk_label} />
                  </div>
                  <p className="mt-1 text-sm text-muted-foreground">{item.why_short ?? item.why}</p>
                </div>
                <div className="text-right text-sm">
                  <p className="font-semibold">{formatPercent(item.fused_confidence)}</p>
                  <p className="text-muted-foreground">Confidence</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Paper Portfolio</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {dashboard.positions.map((item) => (
              <div key={item.ticker} className="grid grid-cols-[1fr_auto] items-center rounded-2xl border border-border/60 p-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold">{item.ticker}</span>
                    {item.action ? <ActionBadge value={item.action} /> : null}
                  </div>
                  <p className="mt-1 text-sm text-muted-foreground">
                    {item.quantity} shares · avg {formatCurrency(item.avg_entry)}
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-semibold">{formatCurrency(item.unrealized_pnl)}</p>
                  <p className="text-sm text-muted-foreground">{formatPercent(item.pnl_pct ?? 0)}</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
