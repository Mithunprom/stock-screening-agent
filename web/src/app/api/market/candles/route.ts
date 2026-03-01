import { NextRequest, NextResponse } from "next/server";

import { getCandles } from "@/lib/server/research-store";

export async function GET(request: NextRequest) {
  const ticker = request.nextUrl.searchParams.get("ticker");
  const interval = request.nextUrl.searchParams.get("interval") ?? "1h";
  const range = request.nextUrl.searchParams.get("range") ?? "1M";
  if (!ticker) {
    return NextResponse.json({ error: "ticker is required" }, { status: 400 });
  }
  const candles = await getCandles(ticker.toUpperCase(), range, interval);
  const availableInterval = ["1m", "5m", "15m", "1h", "1d"].includes(interval) ? interval : "1h";
  return NextResponse.json({
    ticker: ticker.toUpperCase(),
    range,
    interval: availableInterval,
    note: availableInterval === interval ? "Requested interval available." : `Requested ${interval} unavailable; showing ${availableInterval} instead.`,
    candles
  });
}
