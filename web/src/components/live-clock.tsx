"use client";

import { useEffect, useState } from "react";

import { formatRelativeShort } from "@/lib/utils";

export function LiveClock({ updatedAt }: { updatedAt: string }) {
  const [now, setNow] = useState(Date.now());

  useEffect(() => {
    const timer = window.setInterval(() => setNow(Date.now()), 15000);
    return () => window.clearInterval(timer);
  }, []);

  return <span key={now}>Last updated {formatRelativeShort(updatedAt)}</span>;
}
