import { notFound } from "next/navigation";

import { CandlestickPanel } from "@/components/candlestick-panel";
import { NewsFeed } from "@/components/news-feed";
import { ActionBadge, ConvictionBadge, RiskBadge } from "@/components/status-badge";
import { TickerWatchControls } from "@/components/ticker-watch-controls";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getDashboardPayload, getLatestNews, getSignalSummary } from "@/lib/server/research-store";
import { formatCurrency, formatPercent } from "@/lib/utils";

export default async function TickerPage({ params }: { params: Promise<{ ticker: string }> }) {
  const { ticker: rawTicker } = await params;
  const ticker = rawTicker.toUpperCase();
  const dashboard = await getDashboardPayload();
  const item = dashboard.recommendations.find((row) => row.ticker === ticker);
  if (!item) {
    notFound();
  }
  const [signal, news] = await Promise.all([getSignalSummary(ticker), getLatestNews([ticker])]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-primary/80">{item.sector}</p>
          <h1 className="mt-2 font-display text-4xl font-semibold">{ticker}</h1>
          <p className="mt-3 max-w-2xl text-muted-foreground">{item.why}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <ActionBadge value={item.action} />
          <ConvictionBadge value={item.conviction_label} />
          <RiskBadge value={item.risk_label} />
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.3fr_0.7fr]">
        <CandlestickPanel ticker={ticker} />
        <Card>
          <CardHeader>
            <CardTitle>Signal breakdown</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <div className="grid grid-cols-2 gap-3">
              <Stat label="Fused confidence" value={formatPercent(signal.fused)} />
              <Stat label="Price" value={formatCurrency(item.close)} />
              <Stat label="Invalidation" value={formatCurrency(signal.invalidationPrice)} />
              <Stat label="Volatility regime" value={signal.volatilityRegime} />
            </div>
            <div className="rounded-2xl border border-border/60 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Per-model signals</p>
              <div className="mt-3 space-y-2">
                <SignalRow label="Factor" value={signal.signals.factor} />
                <SignalRow label="Time-series" value={signal.signals.timeSeries} />
                <SignalRow label="News" value={signal.signals.news} />
                <SignalRow label="Volatility" value={signal.signals.volatility} />
              </div>
            </div>
            <div className="rounded-2xl border border-border/60 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Why now</p>
              <ul className="mt-3 space-y-2 text-muted-foreground">
                {signal.whyNow.map((point) => (
                  <li key={point}>• {point}</li>
                ))}
              </ul>
            </div>
            <div className="rounded-2xl border border-border/60 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Top drivers</p>
              <div className="mt-3 space-y-3">
                {signal.topDrivers.map((driver) => (
                  <div key={driver.label}>
                    <div className="mb-1 flex items-center justify-between">
                      <span>{driver.label}</span>
                      <span>{driver.value.toFixed(2)}</span>
                    </div>
                    <div className="h-2 rounded-full bg-muted">
                      <div
                        className={`h-2 rounded-full ${driver.value >= 0 ? "bg-primary" : "bg-rose-500"}`}
                        style={{ width: `${Math.min(100, Math.abs(driver.value) * 60)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <TickerWatchControls ticker={ticker} />
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <Card>
          <CardHeader>
            <CardTitle>Key levels and trust markers</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <div className="grid grid-cols-2 gap-3">
              <Stat label="ATR stop proxy" value={formatCurrency(item.invalidation_price)} />
              <Stat label="5D realized vol" value={formatPercent(item.rv_5d)} />
              <Stat label="Average liquidity" value={formatCurrency(item.avg_dollar_volume_20d)} />
              <Stat label="Model freshness" value={new Date(signal.modelFreshness).toLocaleTimeString()} />
            </div>
            <p className="rounded-2xl border border-border/60 p-4 text-muted-foreground">{item.what_changes}</p>
            <p className="rounded-2xl border border-border/60 p-4 text-muted-foreground">{item.caveats}</p>
          </CardContent>
        </Card>
        <NewsFeed items={news} title={`${ticker} catalyst feed`} />
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-border/60 p-4">
      <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">{label}</p>
      <p className="mt-2 font-semibold">{value}</p>
    </div>
  );
}

function SignalRow({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-muted-foreground">{label}</span>
      <span className={value >= 0 ? "text-emerald-500" : "text-rose-500"}>{value.toFixed(2)}</span>
    </div>
  );
}
