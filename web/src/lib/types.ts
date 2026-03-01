export type ActionLabel = "CONSIDER ENTRY" | "WATCH" | "HOLD" | "CONSIDER EXIT";
export type RiskLabel = "OK" | "RISKY";
export type ConvictionLabel = "Low" | "Developing" | "Strong" | "High";

export interface Recommendation {
  ticker: string;
  sector: string;
  action: ActionLabel;
  close: number;
  opportunity_score: number;
  conviction_label: ConvictionLabel;
  hold_horizon: string;
  fused_confidence: number;
  risk_label: RiskLabel;
  rv_5d: number;
  atr_pct: number;
  avg_dollar_volume_20d: number;
  catalyst: string;
  catalyst_confidence?: number;
  event_risk_score?: number;
  xsec_score: number;
  ts_score: number;
  vol_risk_score: number;
  invalidation_price: number;
  why: string;
  what_changes: string;
  caveats: string;
  why_short?: string;
}

export interface WatchlistItem extends Recommendation {
  alertsEnabled?: boolean;
  confidenceDeltaThreshold?: number;
  predictedMoveThreshold?: number;
  cooldownMinutes?: number;
}

export interface NewsItem {
  id: string;
  ticker: string;
  headline: string;
  summary: string;
  impactScore: number;
  publishedAt: string;
  source: string;
  catalyst: string;
}

export interface PortfolioPosition {
  ticker: string;
  quantity: number;
  avg_entry: number;
  mark: number;
  market_value: number;
  unrealized_pnl: number;
  pnl_pct?: number;
  action?: ActionLabel;
  conviction_label?: ConvictionLabel;
  hold_horizon?: string;
  risk_label?: RiskLabel;
  invalidation_price?: number;
}

export interface PortfolioState {
  cash: number;
  day_start_equity: number;
  current_day: string;
  kill_switch_active: boolean;
  realized_pnl: number;
  equityCurve: Array<{ timestamp: string; equity: number }>;
}

export interface MarketContext {
  spy_last: number;
  spy_ret_1d: number;
  spy_rv_5d: number;
  qqq_last: number;
  qqq_ret_1d: number;
  qqq_rv_5d: number;
  risk_regime: string;
}

export interface ModelFreshness {
  factor: string;
  deep: string;
  baseline: string;
  volatility: string;
}

export interface DashboardPayload {
  as_of: string;
  market_context: MarketContext;
  recommendations: Recommendation[];
  watchlist: WatchlistItem[];
  positions: PortfolioPosition[];
  portfolio_state: PortfolioState;
  paper_actions: Array<Record<string, string | number>>;
  news: NewsItem[];
  model_freshness: ModelFreshness;
  data_status: {
    latencyMs: number;
    level: "green" | "yellow" | "red";
    feed: string;
    note: string;
  };
  backtest_summary: {
    ic: number;
    ic_ir: number;
    hit_rate: number;
    disclaimer: string;
  };
}

export interface QuotePayload {
  ticker: string;
  price: number;
  changePct: number;
  updatedAt: string;
  source: string;
}

export interface Candle {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  vwap: number;
  ma20: number;
  ma50: number;
  atrHigh: number;
  atrLow: number;
}

export interface SignalSummary {
  ticker: string;
  fused: number;
  action: ActionLabel;
  riskLabel: RiskLabel;
  invalidationPrice: number;
  volatilityRegime: string;
  signals: {
    factor: number;
    timeSeries: number;
    news: number;
    volatility: number;
  };
  topDrivers: Array<{ label: string; value: number }>;
  whyNow: string[];
  modelFreshness: string;
}

export interface AlertPreference {
  ticker: string;
  enabled: boolean;
  confidenceDeltaThreshold: number;
  predictedMoveThreshold: number;
  riskDowngradeAlert: boolean;
  majorNewsAlert: boolean;
  cooldownMinutes: number;
}

export interface UserPreferences {
  onboardingComplete: boolean;
  riskTolerance: "Conservative" | "Balanced" | "Aggressive";
  alertChannel: "email" | "digest";
  watchlist: AlertPreference[];
}
