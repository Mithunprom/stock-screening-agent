import { NextRequest, NextResponse } from "next/server";

import { saveUserPreferences, getUserPreferences } from "@/lib/server/research-store";
import type { UserPreferences } from "@/lib/types";
import { proxyOrFallback } from "@/lib/server/proxy-route";

export async function GET() {
  return proxyOrFallback("/api/preferences", async () => NextResponse.json(await getUserPreferences()));
}

export async function POST(request: NextRequest) {
  const payload = (await request.json()) as UserPreferences;
  return proxyOrFallback("/api/preferences", async () => {
    const saved = await saveUserPreferences(payload);
    return NextResponse.json(saved);
  }, { method: "POST", body: JSON.stringify(payload) });
}
