"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { signIn } from "next-auth/react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export function LoginForm({ hintEmail }: { hintEmail: string }) {
  const router = useRouter();
  const [email, setEmail] = useState(hintEmail);
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit() {
    setLoading(true);
    setError(null);
    const response = await signIn("credentials", {
      email,
      password,
      redirect: false
    });
    if (!response || response.error) {
      setError(response?.error ?? "Login failed");
      setLoading(false);
      return;
    }
    router.push("/");
    router.refresh();
  }

  return (
    <Card className="mx-auto max-w-md shadow-soft">
      <CardHeader>
        <CardTitle>Log in</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <label className="space-y-2 text-sm">
          <span className="text-muted-foreground">Email</span>
          <Input value={email} onChange={(event) => setEmail(event.target.value)} />
        </label>
        <label className="space-y-2 text-sm">
          <span className="text-muted-foreground">Password</span>
          <Input type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
        </label>
        {error ? <p className="text-sm text-rose-500">{error}</p> : null}
        <Button onClick={submit} className="w-full" disabled={loading}>
          {loading ? "Signing in..." : "Sign in"}
        </Button>
        <p className="text-xs text-muted-foreground">Local mode uses an Auth.js credentials provider. You can switch to GitHub or Google OAuth by setting the auth environment variables.</p>
      </CardContent>
    </Card>
  );
}
