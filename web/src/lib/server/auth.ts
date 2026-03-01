import { auth } from "../../../auth";

export async function getCurrentSession() {
  return auth();
}

export function getDemoCredentials() {
  return {
    email: process.env.APP_DEMO_EMAIL || "demo@stockagent.local",
    password: process.env.APP_DEMO_PASSWORD || "demo-password"
  };
}
