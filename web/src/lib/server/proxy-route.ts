import { NextResponse } from "next/server";

import { proxyBackend } from "@/lib/server/backend";

export async function proxyOrFallback(path: string, fallback: () => Promise<NextResponse>, init?: RequestInit) {
  const proxied = await proxyBackend(path, init);
  if (proxied?.ok) {
    const text = await proxied.text();
    return new NextResponse(text, {
      status: proxied.status,
      headers: {
        "Content-Type": proxied.headers.get("content-type") ?? "application/json"
      }
    });
  }
  return fallback();
}
