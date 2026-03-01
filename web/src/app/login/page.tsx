import { redirect } from "next/navigation";

import { LoginForm } from "@/components/login-form";
import { getCurrentSession, getDemoCredentials } from "@/lib/server/auth";

export default async function LoginPage() {
  const session = await getCurrentSession();
  if (session) {
    redirect("/");
  }
  const creds = getDemoCredentials();
  return (
    <div className="flex min-h-[70vh] items-center justify-center">
      <div className="w-full max-w-lg space-y-6">
        <div className="text-center">
          <p className="text-xs uppercase tracking-[0.24em] text-primary/80">Subscription-ready access</p>
          <h1 className="mt-2 font-display text-4xl font-semibold">Secure the research console</h1>
          <p className="mt-3 text-muted-foreground">Auth.js now gates the app. Local development uses credentials by default, and the config supports GitHub or Google OAuth when those keys are present.</p>
        </div>
        <LoginForm hintEmail={creds.email} />
      </div>
    </div>
  );
}
