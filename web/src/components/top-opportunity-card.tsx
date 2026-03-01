import Link from "next/link";
import type { Route } from "next";
import { ArrowRight } from "lucide-react";

import { ActionBadge, ConvictionBadge, RiskBadge } from "@/components/status-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Recommendation } from "@/lib/types";
import { formatCurrency, formatPercent } from "@/lib/utils";

export function TopOpportunityCard({ item }: { item: Recommendation }) {
  const tickerHref = `/ticker/${item.ticker}` as Route;
  return (
    <Card className="h-full bg-hero-glow">
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">{item.sector}</p>
            <CardTitle className="mt-2 text-2xl">{item.ticker}</CardTitle>
          </div>
          <RiskBadge value={item.risk_label} />
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-wrap gap-2">
          <ActionBadge value={item.action} />
          <ConvictionBadge value={item.conviction_label} />
        </div>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <p className="text-muted-foreground">Price</p>
            <p className="font-semibold">{formatCurrency(item.close)}</p>
          </div>
          <div>
            <p className="text-muted-foreground">Confidence</p>
            <p className="font-semibold">{formatPercent(item.fused_confidence)}</p>
          </div>
          <div>
            <p className="text-muted-foreground">Risk regime</p>
            <p className="font-semibold">{item.vol_risk_score > 0.65 ? "Hot" : "Contained"}</p>
          </div>
          <div>
            <p className="text-muted-foreground">Hold horizon</p>
            <p className="font-semibold">{item.hold_horizon}</p>
          </div>
        </div>
        <ul className="space-y-2 text-sm text-muted-foreground">
          <li>Price action: {item.why_short ?? item.why}</li>
          <li>Volatility: 5D realized vol {formatPercent(item.rv_5d)} with ATR {formatPercent(item.atr_pct)}.</li>
          <li>News: {item.catalyst || "No fresh catalyst"}.</li>
        </ul>
        <Link href={tickerHref} className="inline-flex items-center gap-2 text-sm font-medium text-primary">
          Open detail <ArrowRight className="size-4" />
        </Link>
      </CardContent>
    </Card>
  );
}
