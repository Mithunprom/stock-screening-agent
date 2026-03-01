import { NextRequest, NextResponse } from "next/server";

import { getUserPreferences, updateWatchlistPreference } from "@/lib/server/research-store";
import type { AlertPreference } from "@/lib/types";
import { proxyOrFallback } from "@/lib/server/proxy-route";

export async function GET() {
  return proxyOrFallback("/api/watchlist", async () => {
    const prefs = await getUserPreferences();
    return NextResponse.json(prefs.watchlist);
  });
}

export async function POST(request: NextRequest) {
  const payload = (await request.json()) as AlertPreference;
  return proxyOrFallback("/api/watchlist", async () => {
    const saved = await updateWatchlistPreference(payload);
    return NextResponse.json(saved.watchlist);
  }, { method: "POST", body: JSON.stringify(payload) });
}
