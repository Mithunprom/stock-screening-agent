import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

export default function NotFound() {
  return (
    <div className="flex min-h-[70vh] items-center justify-center">
      <Card className="max-w-lg">
        <CardContent className="space-y-4 p-8 text-center">
          <p className="text-xs uppercase tracking-[0.24em] text-primary/80">Ticker not found</p>
          <h1 className="font-display text-3xl font-semibold">This research view is not available yet.</h1>
          <p className="text-muted-foreground">The requested ticker was not found in the current snapshot. Return to the dashboard or screener and open a tracked name.</p>
          <Button asChild>
            <Link href="/">Back to dashboard</Link>
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
