import { NextRequest, NextResponse } from "next/server";

import { getTopVolatile } from "@/lib/server/research-store";
import { proxyOrFallback } from "@/lib/server/proxy-route";

export async function GET(request: NextRequest) {
  const limit = Number(request.nextUrl.searchParams.get("limit") ?? "20");
  const window = request.nextUrl.searchParams.get("window") ?? "5d";
  return proxyOrFallback(`/api/screener/top-volatile?window=${window}&limit=${limit}`, async () => {
    const rows = await getTopVolatile(limit);
    return NextResponse.json({
      window,
      rows
    });
  });
}
