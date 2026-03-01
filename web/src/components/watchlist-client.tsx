"use client";

import type { AlertPreference } from "@/lib/types";
import { WatchlistSettings } from "@/components/watchlist-settings";

export function WatchlistClient({ items }: { items: AlertPreference[] }) {
  return (
    <WatchlistSettings
      items={items}
      onSave={async (item) => {
        await fetch("/api/watchlist", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(item)
        });
      }}
    />
  );
}
