import { NextRequest, NextResponse } from "next/server";

import { getSignalSummary } from "@/lib/server/research-store";
import { proxyOrFallback } from "@/lib/server/proxy-route";

export async function GET(request: NextRequest) {
  const ticker = request.nextUrl.searchParams.get("ticker");
  if (!ticker) {
    return NextResponse.json({ error: "ticker is required" }, { status: 400 });
  }
  return proxyOrFallback(`/api/signals/summary?ticker=${encodeURIComponent(ticker.toUpperCase())}`, async () => {
    const summary = await getSignalSummary(ticker.toUpperCase());
    return NextResponse.json(summary);
  });
}
