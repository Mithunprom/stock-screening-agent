import { NextRequest, NextResponse } from "next/server";

import { getLatestNews } from "@/lib/server/research-store";

export async function GET(request: NextRequest) {
  const tickers = (request.nextUrl.searchParams.get("tickers") ?? "")
    .split(",")
    .map((item) => item.trim().toUpperCase())
    .filter(Boolean);
  const rows = await getLatestNews(tickers);
  return NextResponse.json({ rows });
}
