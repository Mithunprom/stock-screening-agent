import { NextRequest, NextResponse } from "next/server";

import { getUserPreferences, updateWatchlistPreference } from "@/lib/server/research-store";
import type { AlertPreference } from "@/lib/types";

export async function GET() {
  const prefs = await getUserPreferences();
  return NextResponse.json(prefs.watchlist);
}

export async function POST(request: NextRequest) {
  const payload = (await request.json()) as AlertPreference;
  const saved = await updateWatchlistPreference(payload);
  return NextResponse.json(saved.watchlist);
}
