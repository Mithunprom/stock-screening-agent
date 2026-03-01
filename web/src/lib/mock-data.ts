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

const now = new Date();

const sampleRecommendations: Recommendation[] = [
  {
    ticker: "LMT",
    sector: "Industrials",
    action: "CONSIDER ENTRY",
    close: 487.22,
    opportunity_score: 0.78,
    conviction_label: "High",
    hold_horizon: "3-10 days",
    fused_confidence: 0.74,
    risk_label: "OK",
    rv_5d: 0.34,
    atr_pct: 0.028,
    avg_dollar_volume_20d: 1_280_000_000,
    catalyst: "geopolitical shock",
    catalyst_confidence: 0.86,
    event_risk_score: 0.72,
    xsec_score: 1.24,
    ts_score: 0.67,
    vol_risk_score: 0.41,
    invalidation_price: 472.4,
    why: "Defense flows strengthened after fresh geopolitical headlines, realized volatility remains tradeable, and cross-sectional momentum is leading the sector.",
    what_changes: "A confidence drop below 0.58, a reversal through the invalidation level, or de-escalation in the catalyst tape.",
    caveats: "Headline-driven; expect gap risk if the geopolitical narrative fades.",
    why_short: "Defense tape + positive factor spread + contained risk."
  },
  {
    ticker: "NVDA",
    sector: "Technology",
    action: "WATCH",
    close: 912.33,
    opportunity_score: 0.73,
    conviction_label: "Strong",
    hold_horizon: "1-5 days",
    fused_confidence: 0.69,
    risk_label: "OK",
    rv_5d: 0.49,
    atr_pct: 0.037,
    avg_dollar_volume_20d: 5_200_000_000,
    catalyst: "analyst action",
    catalyst_confidence: 0.71,
    event_risk_score: 0.58,
    xsec_score: 1.08,
    ts_score: 0.51,
    vol_risk_score: 0.54,
    invalidation_price: 880.1,
    why: "Semis remain the leadership group, news tone is constructive, and the ensemble still favors upside despite elevated realized volatility.",
    what_changes: "Loss of semiconductor leadership, risk score above 0.70, or a close below 880.1.",
    caveats: "High-beta name; gaps can outrun stops.",
    why_short: "Leadership sector + supportive analyst tape."
  },
  {
    ticker: "XLE",
    sector: "Energy",
    action: "WATCH",
    close: 95.28,
    opportunity_score: 0.67,
    conviction_label: "Strong",
    hold_horizon: "3-10 days",
    fused_confidence: 0.63,
    risk_label: "OK",
    rv_5d: 0.29,
    atr_pct: 0.022,
    avg_dollar_volume_20d: 890_000_000,
    catalyst: "macro shock",
    catalyst_confidence: 0.59,
    event_risk_score: 0.44,
    xsec_score: 0.92,
    ts_score: 0.4,
    vol_risk_score: 0.35,
    invalidation_price: 92.7,
    why: "Energy is showing better relative momentum, macro-sensitive names are firm, and the volatility regime is still manageable.",
    what_changes: "Oil-sensitive headlines rolling over or XLE closing below 92.7.",
    caveats: "Macro-sensitive; correlation to broader risk assets can rise quickly.",
    why_short: "Sector rotation improving with calmer vol."
  },
  {
    ticker: "AAPL",
    sector: "Technology",
    action: "HOLD",
    close: 188.41,
    opportunity_score: 0.59,
    conviction_label: "Developing",
    hold_horizon: "1-5 days",
    fused_confidence: 0.57,
    risk_label: "OK",
    rv_5d: 0.21,
    atr_pct: 0.018,
    avg_dollar_volume_20d: 3_900_000_000,
    catalyst: "company news",
    catalyst_confidence: 0.44,
    event_risk_score: 0.31,
    xsec_score: 0.66,
    ts_score: 0.22,
    vol_risk_score: 0.28,
    invalidation_price: 183.6,
    why: "Liquidity remains strong and signals lean positive, but upside edge is weaker than the top setups.",
    what_changes: "New product catalyst or a breakout in factor leadership.",
    caveats: "Mega-cap drift can stall without catalyst support.",
    why_short: "Liquid and stable, but less asymmetric."
  },
  {
    ticker: "TSLA",
    sector: "Consumer",
    action: "CONSIDER EXIT",
    close: 176.88,
    opportunity_score: 0.31,
    conviction_label: "Low",
    hold_horizon: "1-3 days",
    fused_confidence: 0.34,
    risk_label: "RISKY",
    rv_5d: 0.71,
    atr_pct: 0.062,
    avg_dollar_volume_20d: 4_400_000_000,
    catalyst: "company news",
    catalyst_confidence: 0.51,
    event_risk_score: 0.81,
    xsec_score: -0.42,
    ts_score: -0.31,
    vol_risk_score: 0.82,
    invalidation_price: 171.1,
    why: "Volatility is elevated, the time-series model rolled over, and the risk engine is now blocking fresh entries.",
    what_changes: "Risk score cooling below 0.65 and confidence recovering above 0.50.",
    caveats: "Can whipsaw quickly around news.",
    why_short: "High vol + risk block + weak signal."
  }
];

const sampleNews: NewsItem[] = [
  {
    id: "n1",
    ticker: "LMT",
    headline: "Defense names firm as new geopolitical risk premium enters the tape",
    summary: "Defense complex outperformed after overnight headlines increased focus on procurement and security spending.",
    impactScore: 84,
    publishedAt: new Date(now.getTime() - 22 * 60000).toISOString(),
    source: "Public RSS",
    catalyst: "geopolitical shock"
  },
  {
    id: "n2",
    ticker: "NVDA",
    headline: "Chip demand narrative remains constructive after fresh analyst upgrades",
    summary: "Analyst tone improved with stronger data-center checks and higher long-term AI infrastructure assumptions.",
    impactScore: 73,
    publishedAt: new Date(now.getTime() - 55 * 60000).toISOString(),
    source: "Public RSS",
    catalyst: "analyst action"
  },
  {
    id: "n3",
    ticker: "XLE",
    headline: "Energy outperforms as macro-sensitive sectors rotate higher",
    summary: "Sector rotation picked up with crude-sensitive names outperforming broad benchmarks.",
    impactScore: 61,
    publishedAt: new Date(now.getTime() - 90 * 60000).toISOString(),
    source: "Public RSS",
    catalyst: "macro shock"
  }
];

const defaultWatchlist: AlertPreference[] = sampleRecommendations.slice(0, 4).map((item) => ({
  ticker: item.ticker,
  enabled: true,
  confidenceDeltaThreshold: 0.07,
  predictedMoveThreshold: 0.04,
  riskDowngradeAlert: true,
  majorNewsAlert: true,
  cooldownMinutes: 90
}));

export function getSamplePreferences(): UserPreferences {
  return {
    onboardingComplete: false,
    riskTolerance: "Balanced",
    alertChannel: "email",
    watchlist: defaultWatchlist
  };
}

export function getSampleDashboard(): DashboardPayload {
  return {
    as_of: now.toISOString(),
    market_context: {
      spy_last: 584.2,
      spy_ret_1d: -0.004,
      spy_rv_5d: 0.19,
      qqq_last: 513.7,
      qqq_ret_1d: 0.006,
      qqq_rv_5d: 0.22,
      risk_regime: "Elevated but tradeable"
    },
    recommendations: [
      ...sampleRecommendations,
      ...sampleRecommendations.map((row, index) => ({
        ...row,
        ticker: `${row.ticker}${index}`,
        opportunity_score: Math.max(0.12, row.opportunity_score - 0.03 * (index + 1)),
        fused_confidence: Math.max(0.18, row.fused_confidence - 0.025 * (index + 1)),
        conviction_label: index > 2 ? "Developing" : row.conviction_label,
        action: index > 2 ? "WATCH" : row.action
      }))
    ].slice(0, 20),
    watchlist: sampleRecommendations.slice(0, 5),
    positions: [
      {
        ticker: "LMT",
        quantity: 1.8,
        avg_entry: 481.4,
        mark: 487.22,
        market_value: 877,
        unrealized_pnl: 10.48,
        pnl_pct: 0.0121,
        action: "CONSIDER ENTRY",
        conviction_label: "High",
        hold_horizon: "3-10 days",
        risk_label: "OK",
        invalidation_price: 472.4
      },
      {
        ticker: "AAPL",
        quantity: 2.5,
        avg_entry: 185.1,
        mark: 188.41,
        market_value: 471.03,
        unrealized_pnl: 8.27,
        pnl_pct: 0.0179,
        action: "HOLD",
        conviction_label: "Developing",
        hold_horizon: "1-5 days",
        risk_label: "OK",
        invalidation_price: 183.6
      }
    ],
    portfolio_state: {
      cash: 612.14,
      day_start_equity: 1965.88,
      current_day: now.toISOString().slice(0, 10),
      kill_switch_active: false,
      realized_pnl: 43.28,
      equityCurve: Array.from({ length: 20 }, (_, index) => ({
        timestamp: new Date(now.getTime() - (19 - index) * 3600 * 1000).toISOString(),
        equity: 1700 + index * 12 + Math.sin(index / 2) * 18
      }))
    },
    paper_actions: [
      { ticker: "LMT", paper_action: "ENTRY", qty: 1.8, price: 481.4 }
    ],
    news: sampleNews,
    model_freshness: {
      factor: new Date(now.getTime() - 55 * 60000).toISOString(),
      deep: new Date(now.getTime() - 80 * 60000).toISOString(),
      baseline: new Date(now.getTime() - 70 * 60000).toISOString(),
      volatility: new Date(now.getTime() - 40 * 60000).toISOString()
    },
    data_status: {
      latencyMs: 850,
      level: "green",
      feed: "sample-mode",
      note: "Using cached snapshot with deterministic sample candles."
    },
    backtest_summary: {
      ic: 0.08,
      ic_ir: 0.64,
      hit_rate: 0.57,
      disclaimer: "Validation metrics are indicative research diagnostics, not a guarantee of future outcomes."
    }
  };
}

export function getSampleQuote(ticker: string): QuotePayload {
  const base = getSampleDashboard().recommendations.find((item) => item.ticker === ticker)?.close ?? 100;
  const bump = ((ticker.charCodeAt(0) % 9) - 4) / 100;
  return {
    ticker,
    price: Number((base * (1 + bump / 10)).toFixed(2)),
    changePct: bump,
    updatedAt: new Date().toISOString(),
    source: "sample-mode"
  };
}

export function getSampleCandles(ticker: string, range: string, interval: string): Candle[] {
  const stepsByRange: Record<string, number> = {
    "1D": 60,
    "5D": 80,
    "1M": 50,
    "6M": 90,
    "1Y": 120
  };
  const count = stepsByRange[range] ?? 60;
  const seed = ticker.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const base = getSampleQuote(ticker).price;
  const candles: Candle[] = [];
  let prevClose = base * 0.94;
  let cumulativeVolume = 0;
  let cumulativePV = 0;

  for (let index = 0; index < count; index += 1) {
    const wave = Math.sin((index + seed) / 7) * 1.8;
    const drift = ((seed % 5) - 2) * 0.08;
    const open = prevClose;
    const close = Math.max(2, open + wave + drift);
    const high = Math.max(open, close) + 1.2 + Math.abs(Math.sin(index)) * 0.6;
    const low = Math.min(open, close) - 1.1 - Math.abs(Math.cos(index)) * 0.4;
    const volume = 400000 + ((seed * (index + 3)) % 1600000);
    cumulativeVolume += volume;
    cumulativePV += close * volume;
    const recentCloses = [...candles.slice(-49).map((item) => item.close), close];
    const ma20 =
      recentCloses.slice(-20).reduce((sum, value) => sum + value, 0) / Math.min(20, recentCloses.length);
    const ma50 =
      recentCloses.slice(-50).reduce((sum, value) => sum + value, 0) / Math.min(50, recentCloses.length);
    const atr = (high - low) * 0.85;
    candles.push({
      time: new Date(now.getTime() - (count - index) * _intervalToMs(interval)).toISOString(),
      open: Number(open.toFixed(2)),
      high: Number(high.toFixed(2)),
      low: Number(low.toFixed(2)),
      close: Number(close.toFixed(2)),
      volume,
      vwap: Number((cumulativePV / cumulativeVolume).toFixed(2)),
      ma20: Number(ma20.toFixed(2)),
      ma50: Number(ma50.toFixed(2)),
      atrHigh: Number((close + atr).toFixed(2)),
      atrLow: Number((close - atr).toFixed(2))
    });
    prevClose = close;
  }
  return candles;
}

export function getSampleSignalSummary(ticker: string): SignalSummary {
  const row = getSampleDashboard().recommendations.find((item) => item.ticker === ticker) ?? sampleRecommendations[0];
  return {
    ticker,
    fused: row.fused_confidence,
    action: row.action,
    riskLabel: row.risk_label,
    invalidationPrice: row.invalidation_price,
    volatilityRegime: row.vol_risk_score > 0.65 ? "Hot" : row.vol_risk_score > 0.45 ? "Active" : "Contained",
    signals: {
      factor: row.xsec_score,
      timeSeries: row.ts_score,
      news: row.event_risk_score ?? 0.4,
      volatility: 1 - row.vol_risk_score
    },
    topDrivers: [
      { label: "Catalyst strength", value: 0.36 },
      { label: "Cross-sectional momentum", value: 0.28 },
      { label: "Volatility penalty", value: -0.19 },
      { label: "Intraday trend", value: 0.13 }
    ],
    whyNow: [
      "Price is holding above the medium-term trend while volatility remains tradeable.",
      "News tone and catalyst intensity improved versus the prior session.",
      "Factor and time-series signals still agree on direction."
    ],
    modelFreshness: new Date(now.getTime() - 40 * 60000).toISOString()
  };
}

function _intervalToMs(interval: string) {
  const mapping: Record<string, number> = {
    "1m": 60_000,
    "5m": 5 * 60_000,
    "15m": 15 * 60_000,
    "1h": 60 * 60_000,
    "1d": 24 * 60 * 60_000
  };
  return mapping[interval] ?? 60 * 60_000;
}
