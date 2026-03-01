"use client";

import { useMemo, useState } from "react";
import Link from "next/link";

import { ActionBadge, ConvictionBadge, RiskBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { Recommendation } from "@/lib/types";
import { formatCurrency, formatPercent } from "@/lib/utils";

export function ScreenerClient({ rows }: { rows: Recommendation[] }) {
  const [query, setQuery] = useState("");
  const [action, setAction] = useState("All");
  const [risk, setRisk] = useState("All");
  const [conviction, setConviction] = useState("All");

  const filtered = useMemo(() => {
    return rows.filter((row) => {
      if (query && !row.ticker.includes(query.toUpperCase()) && !row.sector.toLowerCase().includes(query.toLowerCase())) {
        return false;
      }
      if (action !== "All" && row.action !== action) {
        return false;
      }
      if (risk !== "All" && row.risk_label !== risk) {
        return false;
      }
      if (conviction !== "All" && row.conviction_label !== conviction) {
        return false;
      }
      return true;
    });
  }, [action, conviction, query, risk, rows]);

  async function addToWatchlist(ticker: string) {
    await fetch("/api/watchlist", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ticker,
        enabled: true,
        confidenceDeltaThreshold: 0.07,
        predictedMoveThreshold: 0.04,
        riskDowngradeAlert: true,
        majorNewsAlert: true,
        cooldownMinutes: 90
      })
    });
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-3 lg:grid-cols-4">
        <Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search ticker or sector" />
        <select className="h-10 rounded-xl border border-border bg-background px-3 text-sm" value={action} onChange={(event) => setAction(event.target.value)}>
          {["All", "CONSIDER ENTRY", "WATCH", "HOLD", "CONSIDER EXIT"].map((item) => (
            <option key={item}>{item}</option>
          ))}
        </select>
        <select className="h-10 rounded-xl border border-border bg-background px-3 text-sm" value={risk} onChange={(event) => setRisk(event.target.value)}>
          {["All", "OK", "RISKY"].map((item) => (
            <option key={item}>{item}</option>
          ))}
        </select>
        <select className="h-10 rounded-xl border border-border bg-background px-3 text-sm" value={conviction} onChange={(event) => setConviction(event.target.value)}>
          {["All", "Low", "Developing", "Strong", "High"].map((item) => (
            <option key={item}>{item}</option>
          ))}
        </select>
      </div>

      <div className="overflow-hidden rounded-2xl border border-border/60">
        <div className="max-h-[720px] overflow-auto">
          <table className="w-full min-w-[1320px] text-left text-sm">
            <thead className="sticky top-0 bg-background">
              <tr className="border-b border-border">
                {["Ticker", "Sector", "Action", "Conviction", "Price", "Confidence", "Vol risk", "Catalyst", "Invalidation", "Why", "Watch"].map((head) => (
                  <th key={head} className="px-4 py-3 text-muted-foreground">
                    {head}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((row, index) => (
                <tr key={row.ticker} className={index % 2 === 0 ? "bg-background/40" : "bg-card/40"}>
                  <td className="px-4 py-4 font-semibold">
                    <Link href={`/ticker/${row.ticker}`} className="text-primary">
                      {row.ticker}
                    </Link>
                  </td>
                  <td className="px-4 py-4 text-muted-foreground">{row.sector}</td>
                  <td className="px-4 py-4">
                    <ActionBadge value={row.action} />
                  </td>
                  <td className="px-4 py-4">
                    <ConvictionBadge value={row.conviction_label} />
                  </td>
                  <td className="px-4 py-4">{formatCurrency(row.close)}</td>
                  <td className="px-4 py-4">{formatPercent(row.fused_confidence)}</td>
                  <td className="px-4 py-4">
                    <RiskBadge value={row.risk_label} />
                  </td>
                  <td className="px-4 py-4 text-muted-foreground">{row.catalyst || "None"}</td>
                  <td className="px-4 py-4">{formatCurrency(row.invalidation_price)}</td>
                  <td className="px-4 py-4 max-w-md text-muted-foreground">{row.why}</td>
                  <td className="px-4 py-4">
                    <Button variant="outline" size="sm" onClick={() => addToWatchlist(row.ticker)}>
                      Quick-add
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
