import { NextResponse } from "next/server";

import { getDashboardPayload } from "@/lib/server/research-store";

export async function GET() {
  const payload = await getDashboardPayload();
  return NextResponse.json(payload, {
    headers: {
      "Cache-Control": "s-maxage=10, stale-while-revalidate=30"
    }
  });
}
