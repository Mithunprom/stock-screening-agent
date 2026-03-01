import type { ReactNode } from "react";

import { Card, CardContent } from "@/components/ui/card";

export function MetricCard({ label, value, hint, icon }: { label: string; value: string; hint?: string; icon?: ReactNode }) {
  return (
    <Card className="bg-card/80">
      <CardContent className="p-5">
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span>{label}</span>
          {icon}
        </div>
        <div className="mt-4 font-display text-3xl font-semibold">{value}</div>
        {hint ? <p className="mt-2 text-sm text-muted-foreground">{hint}</p> : null}
      </CardContent>
    </Card>
  );
}
