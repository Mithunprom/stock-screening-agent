import Link from "next/link";

import { ActionBadge, RiskBadge } from "@/components/status-badge";
import type { Recommendation } from "@/lib/types";
import { formatCurrency, formatPercent } from "@/lib/utils";

export function VolatilityTable({ rows }: { rows: Recommendation[] }) {
  return (
    <div className="overflow-hidden rounded-2xl border border-border/60 bg-card/80">
      <div className="max-h-[520px] overflow-auto">
        <table className="w-full min-w-[980px] text-left text-sm">
          <thead className="sticky top-0 z-10 bg-background/95 backdrop-blur">
            <tr className="border-b border-border">
              {["Ticker", "Sector", "Action", "Price", "5D Vol", "ATR %", "Liquidity", "Catalyst", "Confidence", "Risk"].map((head) => (
                <th key={head} className="px-4 py-3 font-medium text-muted-foreground">
                  {head}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, index) => (
              <tr key={row.ticker} className={index % 2 === 0 ? "bg-background/50" : "bg-card/50"}>
                <td className="px-4 py-3 font-medium">
                  <Link href={`/ticker/${row.ticker}`} className="text-primary">
                    {row.ticker}
                  </Link>
                </td>
                <td className="px-4 py-3 text-muted-foreground">{row.sector}</td>
                <td className="px-4 py-3">
                  <ActionBadge value={row.action} />
                </td>
                <td className="px-4 py-3">{formatCurrency(row.close)}</td>
                <td className="px-4 py-3">{formatPercent(row.rv_5d)}</td>
                <td className="px-4 py-3">{formatPercent(row.atr_pct)}</td>
                <td className="px-4 py-3">{formatCurrency(row.avg_dollar_volume_20d)}</td>
                <td className="px-4 py-3 text-muted-foreground">{row.catalyst || "None"}</td>
                <td className="px-4 py-3">{formatPercent(row.fused_confidence)}</td>
                <td className="px-4 py-3">
                  <RiskBadge value={row.risk_label} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
