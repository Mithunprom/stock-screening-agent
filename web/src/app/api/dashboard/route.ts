import { NextResponse } from "next/server";

import { getDashboardPayload } from "@/lib/server/research-store";
import { proxyOrFallback } from "@/lib/server/proxy-route";

export async function GET() {
  return proxyOrFallback("/api/dashboard", async () => {
    const payload = await getDashboardPayload();
    return NextResponse.json(payload, {
      headers: {
        "Cache-Control": "s-maxage=10, stale-while-revalidate=30"
      }
    });
  });
}
