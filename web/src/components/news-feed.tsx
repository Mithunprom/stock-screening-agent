import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { NewsItem } from "@/lib/types";
import { formatRelativeShort } from "@/lib/utils";

export function NewsFeed({ items, title = "News & Catalysts" }: { items: NewsItem[]; title?: string }) {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {items.map((item) => (
          <div key={item.id} className="rounded-2xl border border-border/60 p-4">
            <div className="mb-2 flex items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <Badge variant="default">{item.ticker}</Badge>
                <Badge variant={item.impactScore >= 75 ? "danger" : item.impactScore >= 55 ? "warning" : "subtle"}>{item.impactScore} impact</Badge>
              </div>
              <span className="text-xs text-muted-foreground">{formatRelativeShort(item.publishedAt)}</span>
            </div>
            <p className="font-medium">{item.headline}</p>
            <p className="mt-1 text-sm text-muted-foreground">{item.summary}</p>
            <div className="mt-3 flex items-center justify-between text-xs text-muted-foreground">
              <span>{item.source}</span>
              <Link href={`/ticker/${item.ticker}`} className="text-primary">
                Open ticker
              </Link>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
