import { Badge } from "@/components/ui/badge";
import type { ActionLabel, ConvictionLabel, RiskLabel } from "@/lib/types";

export function ActionBadge({ value }: { value: ActionLabel }) {
  const variant = value === "CONSIDER ENTRY" ? "success" : value === "CONSIDER EXIT" ? "danger" : value === "WATCH" ? "warning" : "subtle";
  return <Badge variant={variant}>{value}</Badge>;
}

export function RiskBadge({ value }: { value: RiskLabel }) {
  return <Badge variant={value === "RISKY" ? "danger" : "success"}>{value}</Badge>;
}

export function ConvictionBadge({ value }: { value: ConvictionLabel }) {
  const variant = value === "High" ? "success" : value === "Strong" ? "default" : value === "Developing" ? "warning" : "subtle";
  return <Badge variant={variant}>{value}</Badge>;
}
