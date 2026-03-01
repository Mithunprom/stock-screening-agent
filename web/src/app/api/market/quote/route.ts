import { NextRequest, NextResponse } from "next/server";

import { getQuote } from "@/lib/server/research-store";
import { proxyOrFallback } from "@/lib/server/proxy-route";

export async function GET(request: NextRequest) {
  const ticker = request.nextUrl.searchParams.get("ticker");
  if (!ticker) {
    return NextResponse.json({ error: "ticker is required" }, { status: 400 });
  }
  return proxyOrFallback(`/api/market/quote?ticker=${encodeURIComponent(ticker.toUpperCase())}`, async () => {
    const payload = await getQuote(ticker.toUpperCase());
    return NextResponse.json(payload, {
      headers: {
        "Cache-Control": "s-maxage=5, stale-while-revalidate=10"
      }
    });
  });
}
