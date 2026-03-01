import { NextResponse } from "next/server";

import { getDashboardPayload } from "@/lib/server/research-store";

export async function GET() {
  const dashboard = await getDashboardPayload();
  return NextResponse.json({
    positions: dashboard.positions,
    state: dashboard.portfolio_state
  });
}
