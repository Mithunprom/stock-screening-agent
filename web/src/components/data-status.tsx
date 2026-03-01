import { Wifi, WifiOff } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatRelativeShort } from "@/lib/utils";

export function DataStatusCard({
  updatedAt,
  latencyMs,
  feed,
  note,
  level
}: {
  updatedAt: string;
  latencyMs: number;
  feed: string;
  note: string;
  level: "green" | "yellow" | "red";
}) {
  const variant = level === "green" ? "success" : level === "yellow" ? "warning" : "danger";
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          Data Health
          <Badge variant={variant}>{level.toUpperCase()}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 text-sm">
        <div className="flex items-center gap-2 text-muted-foreground">
          {level === "red" ? <WifiOff className="size-4" /> : <Wifi className="size-4" />}
          Updated {formatRelativeShort(updatedAt)}
        </div>
        <div className="flex items-center justify-between">
          <span className="text-muted-foreground">Latency</span>
          <span>{latencyMs} ms</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-muted-foreground">Source</span>
          <span>{feed}</span>
        </div>
        <p className="text-muted-foreground">{note}</p>
      </CardContent>
    </Card>
  );
}
