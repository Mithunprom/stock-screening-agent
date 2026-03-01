"use client";

import { useEffect, useState } from "react";

import type { QuotePayload } from "@/lib/types";
import { formatCurrency, formatPercent } from "@/lib/utils";

export function LiveSignalStrip({ tickers }: { tickers: string[] }) {
  const [quotes, setQuotes] = useState<QuotePayload[]>([]);

  useEffect(() => {
    let eventSource: EventSource | null = null;
    const fallbackTimer = window.setInterval(async () => {
      const payload = await Promise.all(
        tickers.map(async (ticker) => {
          const response = await fetch(`/api/market/quote?ticker=${ticker}`, { cache: "no-store" });
          return (await response.json()) as QuotePayload;
        })
      );
      setQuotes(payload);
    }, 15000);

    try {
      eventSource = new EventSource(`/api/stream/updates?tickers=${tickers.join(",")}`);
      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data) as { quotes: QuotePayload[] };
        setQuotes(data.quotes);
      };
    } catch {
      eventSource = null;
    }

    return () => {
      window.clearInterval(fallbackTimer);
      eventSource?.close();
    };
  }, [tickers]);

  if (!quotes.length) {
    return null;
  }

  return (
    <div className="flex gap-3 overflow-x-auto rounded-2xl border border-border/60 bg-card/70 px-4 py-3 text-sm">
      {quotes.map((quote) => (
        <div key={quote.ticker} className="flex min-w-[160px] items-center justify-between gap-3 rounded-xl bg-background/60 px-3 py-2">
          <div>
            <p className="font-semibold">{quote.ticker}</p>
            <p className="text-xs text-muted-foreground">{quote.source}</p>
          </div>
          <div className="text-right">
            <p className="font-semibold">{formatCurrency(quote.price)}</p>
            <p className={quote.changePct >= 0 ? "text-emerald-500" : "text-rose-500"}>{formatPercent(quote.changePct)}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
