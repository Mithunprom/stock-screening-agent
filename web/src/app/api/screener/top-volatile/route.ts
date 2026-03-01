import { NextRequest, NextResponse } from "next/server";

import { getTopVolatile } from "@/lib/server/research-store";

export async function GET(request: NextRequest) {
  const limit = Number(request.nextUrl.searchParams.get("limit") ?? "20");
  const rows = await getTopVolatile(limit);
  return NextResponse.json({
    window: request.nextUrl.searchParams.get("window") ?? "5d",
    rows
  });
}
