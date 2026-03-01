"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { createChart, ColorType, type CandlestickData, type HistogramData, LineStyle } from "lightweight-charts";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Candle } from "@/lib/types";

const ranges = ["1D", "5D", "1M", "6M", "1Y"] as const;
const intervals = ["1m", "5m", "15m", "1h", "1d"] as const;

export function CandlestickPanel({ ticker }: { ticker: string }) {
  const chartRef = useRef<HTMLDivElement | null>(null);
  const [range, setRange] = useState<(typeof ranges)[number]>("1M");
  const [interval, setInterval] = useState<(typeof intervals)[number]>("1h");
  const [candles, setCandles] = useState<Candle[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      const response = await fetch(`/api/market/candles?ticker=${ticker}&range=${range}&interval=${interval}`, { cache: "no-store" });
      const payload = await response.json();
      if (!cancelled) {
        setCandles(payload.candles ?? []);
        setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [ticker, range, interval]);

  const transformed = useMemo(
    () =>
      candles.map((item) => ({
        time: (new Date(item.time).getTime() / 1000) as CandlestickData["time"],
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
        volume: item.volume,
        vwap: item.vwap,
        ma20: item.ma20,
        ma50: item.ma50,
        atrHigh: item.atrHigh,
        atrLow: item.atrLow
      })),
    [candles]
  );

  useEffect(() => {
    if (!chartRef.current) {
      return;
    }
    chartRef.current.innerHTML = "";
    const chart = createChart(chartRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: "transparent" },
        textColor: "#94a3b8"
      },
      grid: {
        vertLines: { color: "rgba(148,163,184,0.12)" },
        horzLines: { color: "rgba(148,163,184,0.12)" }
      },
      rightPriceScale: { borderColor: "rgba(148,163,184,0.18)" },
      timeScale: { borderColor: "rgba(148,163,184,0.18)" },
      crosshair: { vertLine: { color: "#0f766e", width: 1 }, horzLine: { color: "#0f766e", width: 1 } },
      height: 420
    });
    const candleSeries = chart.addCandlestickSeries({
      upColor: "#10b981",
      downColor: "#ef4444",
      borderVisible: false,
      wickUpColor: "#10b981",
      wickDownColor: "#ef4444"
    });
    const volumeSeries = chart.addHistogramSeries({
      priceFormat: { type: "volume" },
      priceScaleId: "",
      color: "rgba(148,163,184,0.5)"
    });
    volumeSeries.priceScale().applyOptions({
      scaleMargins: {
        top: 0.8,
        bottom: 0
      }
    });
    const ma20 = chart.addLineSeries({ color: "#0f766e", lineWidth: 2 });
    const ma50 = chart.addLineSeries({ color: "#d97706", lineWidth: 2 });
    const vwap = chart.addLineSeries({ color: "#a21caf", lineWidth: 2, lineStyle: LineStyle.Dashed });
    const atrHigh = chart.addLineSeries({ color: "rgba(59,130,246,0.5)", lineWidth: 1 });
    const atrLow = chart.addLineSeries({ color: "rgba(59,130,246,0.5)", lineWidth: 1 });

    candleSeries.setData(transformed);
    volumeSeries.setData(
      transformed.map((item) => ({
        time: item.time,
        value: item.volume,
        color: item.close >= item.open ? "rgba(16,185,129,0.38)" : "rgba(239,68,68,0.38)"
      })) as HistogramData[]
    );
    ma20.setData(transformed.map((item) => ({ time: item.time, value: item.ma20 })));
    ma50.setData(transformed.map((item) => ({ time: item.time, value: item.ma50 })));
    vwap.setData(transformed.map((item) => ({ time: item.time, value: item.vwap })));
    atrHigh.setData(transformed.map((item) => ({ time: item.time, value: item.atrHigh })));
    atrLow.setData(transformed.map((item) => ({ time: item.time, value: item.atrLow })));
    chart.timeScale().fitContent();

    const resizeObserver = new ResizeObserver(() => {
      if (chartRef.current) {
        chart.applyOptions({ width: chartRef.current.clientWidth });
      }
    });
    resizeObserver.observe(chartRef.current);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
    };
  }, [transformed]);

  return (
    <Card>
      <CardHeader className="space-y-4">
        <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
          <CardTitle>{ticker} price</CardTitle>
          <div className="flex flex-wrap gap-2">
            {ranges.map((item) => (
              <Button key={item} size="sm" variant={range === item ? "default" : "outline"} onClick={() => setRange(item)}>
                {item}
              </Button>
            ))}
            {intervals.map((item) => (
              <Button key={item} size="sm" variant={interval === item ? "secondary" : "outline"} onClick={() => setInterval(item)}>
                {item}
              </Button>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {loading ? <div className="rounded-2xl border border-dashed border-border p-12 text-center text-sm text-muted-foreground">Loading candles...</div> : <div ref={chartRef} className="w-full" />}
      </CardContent>
    </Card>
  );
}
