import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

import { createSession, getDemoCredentials, sessionCookieName } from "@/lib/server/auth";

export async function POST(request: NextRequest) {
  const { email, password } = await request.json();
  const creds = getDemoCredentials();
  if (email !== creds.email || password !== creds.password) {
    return NextResponse.json({ error: "Invalid credentials" }, { status: 401 });
  }
  const cookieStore = await cookies();
  cookieStore.set(sessionCookieName(), createSession(email), {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 60 * 60 * 24 * 14
  });
  return NextResponse.json({ ok: true });
}
