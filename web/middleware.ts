import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

import { sessionCookieName, verifySession } from "@/lib/server/auth";

const PUBLIC_PATHS = ["/login", "/pricing"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  if (pathname.startsWith("/_next") || pathname.startsWith("/favicon") || pathname.startsWith("/api/auth")) {
    return NextResponse.next();
  }
  if (PUBLIC_PATHS.some((path) => pathname === path || pathname.startsWith(`${path}/`))) {
    return NextResponse.next();
  }
  const token = request.cookies.get(sessionCookieName())?.value;
  const session = verifySession(token);
  if (!session) {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!.*\\..*).*)"]
};
