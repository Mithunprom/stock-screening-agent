"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function TickerWatchControls({ ticker }: { ticker: string }) {
  const [confidenceDeltaThreshold, setConfidenceDeltaThreshold] = useState(0.07);
  const [predictedMoveThreshold, setPredictedMoveThreshold] = useState(0.04);
  const [status, setStatus] = useState("Add to watchlist");

  async function save() {
    setStatus("Saving...");
    const response = await fetch("/api/watchlist", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ticker,
        enabled: true,
        confidenceDeltaThreshold,
        predictedMoveThreshold,
        riskDowngradeAlert: true,
        majorNewsAlert: true,
        cooldownMinutes: 90
      })
    });
    setStatus(response.ok ? "Saved" : "Retry");
  }

  return (
    <div className="space-y-3 rounded-2xl border border-border/60 p-4">
      <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Track this ticker</p>
      <div className="grid grid-cols-2 gap-3">
        <label className="space-y-2 text-sm">
          <span className="text-muted-foreground">Confidence delta</span>
          <Input type="number" step="0.01" value={confidenceDeltaThreshold} onChange={(event) => setConfidenceDeltaThreshold(Number(event.target.value))} />
        </label>
        <label className="space-y-2 text-sm">
          <span className="text-muted-foreground">Predicted move</span>
          <Input type="number" step="0.01" value={predictedMoveThreshold} onChange={(event) => setPredictedMoveThreshold(Number(event.target.value))} />
        </label>
      </div>
      <Button onClick={save} className="w-full">
        {status}
      </Button>
    </div>
  );
}
