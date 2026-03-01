"use client";

import { useState } from "react";

import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import type { AlertPreference } from "@/lib/types";

export function WatchlistSettings({
  items,
  onSave
}: {
  items: AlertPreference[];
  onSave: (item: AlertPreference) => Promise<void>;
}) {
  const [savingTicker, setSavingTicker] = useState<string | null>(null);

  return (
    <div className="space-y-4">
      {items.map((item) => (
        <div key={item.ticker} className="grid gap-4 rounded-2xl border border-border/60 bg-card/80 p-4 lg:grid-cols-[1.4fr_repeat(6,1fr)_auto]">
          <div>
            <p className="font-semibold">{item.ticker}</p>
            <p className="text-sm text-muted-foreground">Alert controls for hourly digests and major catalyst updates.</p>
          </div>
          <label className="space-y-2 text-sm">
            <span className="text-muted-foreground">Enabled</span>
            <div>
              <Switch checked={item.enabled} onCheckedChange={(checked) => onSave({ ...item, enabled: checked })} />
            </div>
          </label>
          <label className="space-y-2 text-sm">
            <span className="text-muted-foreground">Major news</span>
            <div>
              <Switch checked={item.majorNewsAlert} onCheckedChange={(checked) => onSave({ ...item, majorNewsAlert: checked })} />
            </div>
          </label>
          <label className="space-y-2 text-sm">
            <span className="text-muted-foreground">Risk downgrade</span>
            <div>
              <Switch checked={item.riskDowngradeAlert} onCheckedChange={(checked) => onSave({ ...item, riskDowngradeAlert: checked })} />
            </div>
          </label>
          <label className="space-y-2 text-sm">
            <span className="text-muted-foreground">Confidence delta</span>
            <Input
              type="number"
              step="0.01"
              defaultValue={item.confidenceDeltaThreshold}
              onBlur={async (event) => {
                setSavingTicker(item.ticker);
                await onSave({ ...item, confidenceDeltaThreshold: Number(event.target.value) });
                setSavingTicker(null);
              }}
            />
          </label>
          <label className="space-y-2 text-sm">
            <span className="text-muted-foreground">Predicted move</span>
            <Input
              type="number"
              step="0.01"
              defaultValue={item.predictedMoveThreshold}
              onBlur={async (event) => {
                setSavingTicker(item.ticker);
                await onSave({ ...item, predictedMoveThreshold: Number(event.target.value) });
                setSavingTicker(null);
              }}
            />
          </label>
          <label className="space-y-2 text-sm">
            <span className="text-muted-foreground">Cooldown mins</span>
            <Input
              type="number"
              step="5"
              defaultValue={item.cooldownMinutes}
              onBlur={async (event) => {
                setSavingTicker(item.ticker);
                await onSave({ ...item, cooldownMinutes: Number(event.target.value) });
                setSavingTicker(null);
              }}
            />
          </label>
          <div className="flex items-end">
            <Button variant="outline" disabled={savingTicker === item.ticker}>
              {savingTicker === item.ticker ? "Saving..." : "Saved"}
            </Button>
          </div>
        </div>
      ))}
    </div>
  );
}
