"use client";

import { useEffect, useMemo, useState } from "react";
import * as Dialog from "@radix-ui/react-dialog";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import type { UserPreferences } from "@/lib/types";

export function OnboardingWizard({
  preferences,
  recommendedTickers
}: {
  preferences: UserPreferences;
  recommendedTickers: string[];
}) {
  const [open, setOpen] = useState(false);
  const [riskTolerance, setRiskTolerance] = useState(preferences.riskTolerance);
  const [tickers, setTickers] = useState(recommendedTickers.slice(0, 5).join(", "));

  useEffect(() => {
    setOpen(!preferences.onboardingComplete);
  }, [preferences.onboardingComplete]);

  const selectedTickers = useMemo(
    () =>
      tickers
        .split(",")
        .map((value) => value.trim().toUpperCase())
        .filter(Boolean),
    [tickers]
  );

  async function completeOnboarding() {
    const response = await fetch("/api/preferences", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...preferences,
        onboardingComplete: true,
        riskTolerance,
        watchlist: selectedTickers.map((ticker) => ({
          ticker,
          enabled: true,
          confidenceDeltaThreshold: 0.07,
          predictedMoveThreshold: 0.04,
          riskDowngradeAlert: true,
          majorNewsAlert: true,
          cooldownMinutes: 90
        }))
      })
    });
    if (response.ok) {
      setOpen(false);
      window.location.reload();
    }
  }

  return (
    <Dialog.Root open={open}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm" />
        <Dialog.Content className="fixed left-1/2 top-1/2 z-50 w-[min(720px,92vw)] -translate-x-1/2 -translate-y-1/2">
          <Card className="border-border/80 shadow-soft">
            <CardContent className="space-y-6 p-8">
              <div>
                <p className="text-xs uppercase tracking-[0.24em] text-primary/80">First-run setup</p>
                <h2 className="mt-2 font-display text-3xl font-semibold">Personalize your research desk</h2>
                <p className="mt-3 text-sm text-muted-foreground">Pick the names, risk posture, and alert defaults you want the app to optimize around.</p>
              </div>
              <div className="grid gap-4 lg:grid-cols-2">
                <label className="space-y-2 text-sm">
                  <span className="text-muted-foreground">Risk tolerance</span>
                  <select
                    className="h-10 w-full rounded-xl border border-border bg-background px-3"
                    value={riskTolerance}
                    onChange={(event) => setRiskTolerance(event.target.value as UserPreferences["riskTolerance"])}
                  >
                    <option>Conservative</option>
                    <option>Balanced</option>
                    <option>Aggressive</option>
                  </select>
                </label>
                <label className="space-y-2 text-sm">
                  <span className="text-muted-foreground">Watchlist tickers</span>
                  <Input value={tickers} onChange={(event) => setTickers(event.target.value)} placeholder="AAPL, NVDA, LMT, XLE" />
                </label>
              </div>
              <div className="rounded-2xl bg-muted/60 p-4 text-sm text-muted-foreground">
                The app will use these names for hourly digest prioritization, major-news alerts, and the watchlist page. You can edit them later.
              </div>
              <div className="flex justify-end">
                <Button onClick={completeOnboarding}>Start the console</Button>
              </div>
            </CardContent>
          </Card>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
