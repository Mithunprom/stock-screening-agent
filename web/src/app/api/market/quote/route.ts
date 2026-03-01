import { NextRequest, NextResponse } from "next/server";

import { getQuote } from "@/lib/server/research-store";

export async function GET(request: NextRequest) {
  const ticker = request.nextUrl.searchParams.get("ticker");
  if (!ticker) {
    return NextResponse.json({ error: "ticker is required" }, { status: 400 });
  }
  const payload = await getQuote(ticker.toUpperCase());
  return NextResponse.json(payload, {
    headers: {
      "Cache-Control": "s-maxage=5, stale-while-revalidate=10"
    }
  });
}
