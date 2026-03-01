import { cookies } from "next/headers";
import crypto from "crypto";

const SESSION_COOKIE = "ssa_session";
const DEFAULT_EMAIL = process.env.APP_DEMO_EMAIL || "demo@stockagent.local";
const DEFAULT_PASSWORD = process.env.APP_DEMO_PASSWORD || "demo-password";
const SESSION_SECRET = process.env.APP_SESSION_SECRET || "development-session-secret";

function sign(value: string) {
  return crypto.createHmac("sha256", SESSION_SECRET).update(value).digest("hex");
}

export function getDemoCredentials() {
  return { email: DEFAULT_EMAIL, password: DEFAULT_PASSWORD };
}

export function createSession(email: string) {
  return Buffer.from(`${email}.${sign(email)}`).toString("base64url");
}

export function verifySession(token: string | undefined | null) {
  if (!token) {
    return null;
  }
  try {
    const raw = Buffer.from(token, "base64url").toString("utf8");
    const [email, signature] = raw.split(".");
    if (!email || !signature) {
      return null;
    }
    if (sign(email) !== signature) {
      return null;
    }
    return { email };
  } catch {
    return null;
  }
}

export async function getCurrentSession() {
  const cookieStore = await cookies();
  return verifySession(cookieStore.get(SESSION_COOKIE)?.value);
}

export function sessionCookieName() {
  return SESSION_COOKIE;
}
