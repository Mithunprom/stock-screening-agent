import { NextRequest, NextResponse } from "next/server";

import { saveUserPreferences, getUserPreferences } from "@/lib/server/research-store";
import type { UserPreferences } from "@/lib/types";

export async function GET() {
  return NextResponse.json(await getUserPreferences());
}

export async function POST(request: NextRequest) {
  const payload = (await request.json()) as UserPreferences;
  const saved = await saveUserPreferences(payload);
  return NextResponse.json(saved);
}
