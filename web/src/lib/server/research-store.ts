import fs from "fs/promises";
import path from "path";

import {
  getSampleCandles,
  getSampleDashboard,
  getSamplePreferences,
  getSampleQuote,
  getSampleSignalSummary
} from "@/lib/mock-data";
import type {
  AlertPreference,
  Candle,
  DashboardPayload,
  NewsItem,
  QuotePayload,
  Recommendation,
  SignalSummary,
  UserPreferences
} from "@/lib/types";
import { withCache } from "@/lib/server/cache";

const repoRoot = path.resolve(process.cwd(), "..");
const sharedDir = path.join(repoRoot, ".state", "shared");

function sharedPath(name: string) {
  return path.join(sharedDir, `${name}.json`);
}

async function readJson<T>(name: string): Promise<T | null> {
  try {
    const raw = await fs.readFile(sharedPath(name), "utf8");
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

async function writeJson(name: string, payload: unknown) {
  await fs.mkdir(sharedDir, { recursive: true });
  await fs.writeFile(sharedPath(name), JSON.stringify(payload, null, 2), "utf8");
}

export async function getDashboardPayload(): Promise<DashboardPayload> {
  return withCache("dashboard", 15_000, async () => {
    const latest = await readJson<Record<string, unknown>>("latest_snapshot");
    const hourly = await readJson<Record<string, unknown>>("hourly_state");
    if (!latest) {
      return getSampleDashboard();
    }
    const sample = getSampleDashboard();
    const recommendations = normalizeRecommendations((latest.recommendations as Recommendation[]) ?? sample.recommendations);
    const watchlist = normalizeRecommendations((latest.watchlist as Recommendation[]) ?? recommendations.slice(0, 5));
    const news = buildNewsFromRecommendations(recommendations);
    return {
      ...sample,
      as_of: String(latest.as_of ?? sample.as_of),
      market_context: (latest.market_context as DashboardPayload["market_context"]) ?? sample.market_context,
      recommendations,
      watchlist,
      positions: (latest.positions as DashboardPayload["positions"]) ?? sample.positions,
      portfolio_state: {
        ...(sample.portfolio_state ?? {}),
        ...((latest.portfolio_state as DashboardPayload["portfolio_state"]) ?? {})
      },
      paper_actions: (latest.paper_actions as DashboardPayload["paper_actions"]) ?? sample.paper_actions,
      news,
      data_status: {
        latencyMs: 420,
        level: latest ? "green" : "yellow",
        feed: latest ? "shared-state snapshot" : "sample-mode",
        note: latest ? "Backed by the research pipeline snapshot with cached market candles." : sample.data_status.note
      },
      model_freshness: sample.model_freshness,
      backtest_summary: sample.backtest_summary
    };
  });
}

export async function getQuote(ticker: string): Promise<QuotePayload> {
  return withCache(`quote:${ticker}`, 5_000, async () => {
    const dashboard = await getDashboardPayload();
    const row = dashboard.recommendations.find((item) => item.ticker === ticker);
    if (!row) {
      return getSampleQuote(ticker);
    }
    return {
      ticker,
      price: row.close,
      changePct: (row.ts_score || 0) / 10,
      updatedAt: dashboard.as_of,
      source: dashboard.data_status.feed
    };
  });
}

export async function getCandles(ticker: string, range: string, interval: string): Promise<Candle[]> {
  return withCache(`candles:${ticker}:${range}:${interval}`, 20_000, async () => getSampleCandles(ticker, range, interval));
}

export async function getTopVolatile(limit = 20): Promise<Recommendation[]> {
  const dashboard = await getDashboardPayload();
  return [...dashboard.recommendations]
    .sort((a, b) => (b.rv_5d ?? 0) - (a.rv_5d ?? 0))
    .slice(0, limit);
}

export async function getLatestNews(tickers: string[] = []): Promise<NewsItem[]> {
  const dashboard = await getDashboardPayload();
  const feed = dashboard.news.length ? dashboard.news : buildNewsFromRecommendations(dashboard.recommendations);
  if (!tickers.length) {
    return feed;
  }
  return feed.filter((item) => tickers.includes(item.ticker));
}

export async function getSignalSummary(ticker: string): Promise<SignalSummary> {
  const dashboard = await getDashboardPayload();
  const row = dashboard.recommendations.find((item) => item.ticker === ticker);
  if (!row) {
    return getSampleSignalSummary(ticker);
  }
  const driverRows = [
    { label: "Factor spread", value: row.xsec_score },
    { label: "Time-series edge", value: row.ts_score },
    { label: "News impact", value: row.event_risk_score ?? 0 },
    { label: "Volatility penalty", value: -(row.vol_risk_score ?? 0) }
  ];
  return {
    ticker,
    fused: row.fused_confidence,
    action: row.action,
    riskLabel: row.risk_label,
    invalidationPrice: row.invalidation_price,
    volatilityRegime: row.vol_risk_score > 0.7 ? "Hot" : row.vol_risk_score > 0.45 ? "Active" : "Contained",
    signals: {
      factor: row.xsec_score,
      timeSeries: row.ts_score,
      news: row.event_risk_score ?? 0,
      volatility: 1 - row.vol_risk_score
    },
    topDrivers: driverRows,
    whyNow: [
      row.why_short ?? "Price action and factor breadth are supportive.",
      `Invalidation sits near ${row.invalidation_price.toFixed(2)} with ${row.hold_horizon} horizon.`,
      row.catalyst ? `News catalyst: ${row.catalyst}.` : "No major fresh catalyst, setup is mostly driven by price/vol."
    ],
    modelFreshness: dashboard.model_freshness.factor
  };
}

export async function getUserPreferences(): Promise<UserPreferences> {
  const stored = await readJson<UserPreferences>("frontend_preferences");
  if (stored) {
    return stored;
  }
  return getSamplePreferences();
}

export async function saveUserPreferences(preferences: UserPreferences): Promise<UserPreferences> {
  await writeJson("frontend_preferences", preferences);
  return preferences;
}

export async function updateWatchlistPreference(payload: AlertPreference): Promise<UserPreferences> {
  const preferences = await getUserPreferences();
  const next = preferences.watchlist.filter((item) => item.ticker !== payload.ticker);
  next.unshift(payload);
  const saved = { ...preferences, watchlist: next };
  await saveUserPreferences(saved);
  return saved;
}

function normalizeRecommendations(rows: Recommendation[]): Recommendation[] {
  return rows.map((row, index) => ({
    ...getSampleDashboard().recommendations[index % getSampleDashboard().recommendations.length],
    ...row
  }));
}

function buildNewsFromRecommendations(recommendations: Recommendation[]): NewsItem[] {
  return recommendations.slice(0, 12).map((row, index) => ({
    id: `${row.ticker}-${index}`,
    ticker: row.ticker,
    headline: `${row.ticker} flagged by fused signals with ${row.conviction_label.toLowerCase()} conviction`,
    summary: row.why,
    impactScore: Math.round(Math.min(99, (row.fused_confidence * 70 + (row.event_risk_score ?? 0.3) * 30))),
    publishedAt: new Date(Date.now() - index * 18 * 60000).toISOString(),
    source: "Research snapshot",
    catalyst: row.catalyst || "company news"
  }));
}
