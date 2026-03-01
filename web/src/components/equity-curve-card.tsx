"use client";

import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatCurrency } from "@/lib/utils";

export function EquityCurveCard({ data }: { data: Array<{ timestamp: string; equity: number }> }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Equity curve</CardTitle>
      </CardHeader>
      <CardContent className="h-[320px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="equity" x1="0" x2="0" y1="0" y2="1">
                <stop offset="5%" stopColor="#0f766e" stopOpacity={0.42} />
                <stop offset="95%" stopColor="#0f766e" stopOpacity={0.03} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="rgba(148,163,184,0.12)" vertical={false} />
            <XAxis dataKey="timestamp" hide />
            <YAxis tickFormatter={(value) => `$${value.toFixed(0)}`} />
            <Tooltip formatter={(value: number) => formatCurrency(value)} labelFormatter={(label) => new Date(label).toLocaleString()} />
            <Area type="monotone" dataKey="equity" stroke="#0f766e" fill="url(#equity)" strokeWidth={2.5} />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
