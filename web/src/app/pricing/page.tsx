import { Check } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const tiers = [
  {
    name: "Starter",
    price: "$19",
    description: "Daily dashboard, watchlist, and morning briefing surfaces.",
    features: ["Dashboard + screener", "Top opportunities", "Watchlist alerts", "Sample-mode access"]
  },
  {
    name: "Research Pro",
    price: "$49",
    description: "Full ticker detail, hourly digest, major-news alerts, and paper portfolio.",
    features: ["Everything in Starter", "Hourly digests", "Major-catalyst alerts", "Paper portfolio + risk guardrails"]
  },
  {
    name: "Team",
    price: "Custom",
    description: "Shared watchlists, API access, and admin features.",
    features: ["Everything in Research Pro", "Seat management", "Audit logs", "SSO / billing integration later"]
  }
];

export default function PricingPage() {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <p className="text-xs uppercase tracking-[0.24em] text-primary/80">Pricing</p>
        <h1 className="mt-2 font-display text-4xl font-semibold">Subscription-ready plan scaffolding</h1>
        <p className="mt-3 text-muted-foreground">No billing provider is wired yet, but the UI structure is ready for it.</p>
      </div>
      <div className="grid gap-6 xl:grid-cols-3">
        {tiers.map((tier) => (
          <Card key={tier.name} className={tier.name === "Research Pro" ? "border-primary shadow-soft" : ""}>
            <CardHeader>
              <CardTitle>{tier.name}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="font-display text-4xl font-semibold">{tier.price}</p>
                <p className="text-sm text-muted-foreground">{tier.description}</p>
              </div>
              <ul className="space-y-2 text-sm">
                {tier.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-2">
                    <Check className="size-4 text-primary" />
                    {feature}
                  </li>
                ))}
              </ul>
              <Button className="w-full" variant={tier.name === "Research Pro" ? "default" : "outline"}>
                {tier.name === "Team" ? "Contact sales later" : "Choose plan later"}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
