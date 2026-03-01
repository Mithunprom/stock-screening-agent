import { AlertTriangle, ShieldCheck } from "lucide-react";

import { ActionBadge, RiskBadge } from "@/components/status-badge";
import { EquityCurveCard } from "@/components/equity-curve-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getDashboardPayload } from "@/lib/server/research-store";
import { formatCurrency, formatPercent } from "@/lib/utils";

export default async function PortfolioPage() {
  const dashboard = await getDashboardPayload();

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs uppercase tracking-[0.24em] text-primary/80">Paper Portfolio</p>
        <h1 className="mt-2 font-display text-4xl font-semibold">Track paper positions with visible risk rules and refreshable P&amp;L.</h1>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <EquityCurveCard data={dashboard.portfolio_state.equityCurve} />
        <Card>
          <CardHeader>
            <CardTitle>Risk status</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <div className="flex items-center justify-between rounded-2xl border border-border/60 p-4">
              <div className="flex items-center gap-3">
                {dashboard.portfolio_state.kill_switch_active ? <AlertTriangle className="size-5 text-amber-500" /> : <ShieldCheck className="size-5 text-emerald-500" />}
                <div>
                  <p className="font-semibold">Daily drawdown freeze</p>
                  <p className="text-muted-foreground">New paper entries stop if intraday drawdown reaches 10%.</p>
                </div>
              </div>
              <RiskBadge value={dashboard.portfolio_state.kill_switch_active ? "RISKY" : "OK"} />
            </div>
            <div className="grid gap-3 rounded-2xl border border-border/60 p-4">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Cash</span>
                <span>{formatCurrency(dashboard.portfolio_state.cash)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Realized P&amp;L</span>
                <span>{formatCurrency(dashboard.portfolio_state.realized_pnl)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Day-start equity</span>
                <span>{formatCurrency(dashboard.portfolio_state.day_start_equity)}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Held positions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {dashboard.positions.map((item) => (
            <div key={item.ticker} className="grid gap-4 rounded-2xl border border-border/60 p-4 lg:grid-cols-[1.3fr_repeat(4,1fr)]">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-semibold">{item.ticker}</span>
                  {item.action ? <ActionBadge value={item.action} /> : null}
                  {item.risk_label ? <RiskBadge value={item.risk_label} /> : null}
                </div>
                <p className="mt-1 text-sm text-muted-foreground">Invalidation near {formatCurrency(item.invalidation_price ?? 0)}</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Quantity</p>
                <p className="mt-2 font-semibold">{item.quantity}</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Mark</p>
                <p className="mt-2 font-semibold">{formatCurrency(item.mark)}</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Unrealized</p>
                <p className="mt-2 font-semibold">{formatCurrency(item.unrealized_pnl)}</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Return</p>
                <p className="mt-2 font-semibold">{formatPercent(item.pnl_pct ?? 0)}</p>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
