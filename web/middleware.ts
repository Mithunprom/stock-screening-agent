import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

import { auth } from "./auth";

const PUBLIC_PATHS = ["/login", "/pricing"];

export default auth((request: NextRequest & { auth?: unknown }) => {
  const { pathname } = request.nextUrl;
  if (pathname.startsWith("/_next") || pathname.startsWith("/favicon") || pathname.startsWith("/api/auth")) {
    return NextResponse.next();
  }
  if (PUBLIC_PATHS.some((path) => pathname === path || pathname.startsWith(`${path}/`))) {
    return NextResponse.next();
  }
  if (!request.auth) {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  return NextResponse.next();
});

export const config = {
  matcher: ["/((?!.*\\..*).*)"]
};
