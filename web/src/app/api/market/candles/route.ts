import { NextRequest, NextResponse } from "next/server";

import { proxyBackend } from "@/lib/server/backend";
import { getCandles } from "@/lib/server/research-store";

export async function GET(request: NextRequest) {
  const ticker = request.nextUrl.searchParams.get("ticker");
  const interval = request.nextUrl.searchParams.get("interval") ?? "1h";
  const rangeParam = request.nextUrl.searchParams.get("range") ?? "1M";
  if (!ticker) {
    return NextResponse.json({ error: "ticker is required" }, { status: 400 });
  }

  const proxyPath = `/api/market/candles?ticker=${encodeURIComponent(ticker.toUpperCase())}&interval=${encodeURIComponent(interval)}&range=${encodeURIComponent(rangeParam)}`;
  const proxied = await proxyBackend(proxyPath);
  if (proxied?.ok) {
    const text = await proxied.text();
    return new NextResponse(text, {
      status: proxied.status,
      headers: {
        "Content-Type": proxied.headers.get("content-type") ?? "application/json"
      }
    });
  }

  const candles = await getCandles(ticker.toUpperCase(), rangeParam, interval);
  const availableInterval = ["1m", "5m", "15m", "1h", "1d"].includes(interval) ? interval : "1h";
  return NextResponse.json({
    ticker: ticker.toUpperCase(),
    range: rangeParam,
    interval: availableInterval,
    note: availableInterval === interval ? "Requested interval available." : `Requested ${interval} unavailable; showing ${availableInterval} instead.`,
    candles
  });
}
