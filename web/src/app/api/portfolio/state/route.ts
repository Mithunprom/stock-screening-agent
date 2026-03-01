import { NextResponse } from "next/server";

import { getDashboardPayload } from "@/lib/server/research-store";
import { proxyOrFallback } from "@/lib/server/proxy-route";

export async function GET() {
  return proxyOrFallback("/api/portfolio/state", async () => {
    const dashboard = await getDashboardPayload();
    return NextResponse.json({
      positions: dashboard.positions,
      state: dashboard.portfolio_state
    });
  });
}
