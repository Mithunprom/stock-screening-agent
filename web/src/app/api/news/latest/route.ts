import { NextRequest, NextResponse } from "next/server";

import { getLatestNews } from "@/lib/server/research-store";
import { proxyOrFallback } from "@/lib/server/proxy-route";

export async function GET(request: NextRequest) {
  const tickers = (request.nextUrl.searchParams.get("tickers") ?? "")
    .split(",")
    .map((item) => item.trim().toUpperCase())
    .filter(Boolean);
  return proxyOrFallback(`/api/news/latest?tickers=${tickers.join(",")}`, async () => {
    const rows = await getLatestNews(tickers);
    return NextResponse.json({ rows });
  });
}
