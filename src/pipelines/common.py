from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import numpy as np
import pandas as pd

from src.config import AppConfig
from src.data.market_data import MarketDataAdapter
from src.data.news_data import NewsDataAdapter
from src.features.build_features import build_feature_frame
from src.features.universe import filter_universe
from src.models.baseline_model import BaselineModel
from src.models.deep_model import DeepTimeSeriesModel
from src.models.explain import Explainer
from src.models.factor_model import FactorModel
from src.models.fusion import FusionModel
from src.models.vol_model import VolModel
from src.portfolio.execution_rules import ExecutionRules
from src.portfolio.paper_portfolio import PaperPortfolio
from src.portfolio.risk import RiskEngine
from src.utils.logging import get_logger
from src.utils.time import now_local

logger = get_logger(__name__)


@dataclass(slots=True)
class PipelineArtifacts:
    as_of: datetime
    daily: pd.DataFrame
    intraday: pd.DataFrame
    latest: pd.DataFrame
    watchlist: pd.DataFrame
    market_context: dict
    portfolio_metrics: dict
    paper_actions: list[dict]
    model_cards: dict


def build_pipeline_artifacts(settings: AppConfig) -> PipelineArtifacts:
    market = MarketDataAdapter(settings)
    news = NewsDataAdapter(settings)
    as_of = now_local(settings.timezone)
    daily = market.fetch_daily_history(settings.universe.tickers)
    universe = filter_universe(daily, settings)
    daily = daily[daily["ticker"].isin(universe)].copy()
    intraday = market.fetch_intraday_history(universe, interval=settings.intraday_interval)
    features = build_feature_frame(daily, intraday)

    factor_model = FactorModel()
    factor_df = factor_model.fit_predict(features)
    deep_model = DeepTimeSeriesModel()
    ts_df = deep_model.fit_predict(features).signal
    vol_df = VolModel().fit_predict(features)
    baseline_df = BaselineModel().fit_predict(features)

    latest = (
        features.sort_values("date").groupby("ticker").tail(1)
        .merge(factor_df[["date", "ticker", "xsec_score"]], on=["date", "ticker"], how="left")
        .merge(ts_df, on=["date", "ticker"], how="left")
        .merge(vol_df, on=["date", "ticker"], how="left")
        .merge(baseline_df, on=["date", "ticker"], how="left")
    )

    news_summary = news.summarize(news.fetch_news(latest["ticker"].tolist()))
    latest = latest.merge(news_summary, on="ticker", how="left")
    latest["event_score"] = latest["sentiment"].fillna(0) * (1 + latest["headline_count"].fillna(0).clip(upper=4) / 4)

    fused = FusionModel().fuse(latest, factor_model.validation)
    risk_engine = RiskEngine(settings)
    latest = risk_engine.classify_risk(fused)

    portfolio = PaperPortfolio(settings)
    portfolio_metrics = portfolio.mark_to_market(dict(zip(latest["ticker"], latest["close"])), as_of)
    rules = ExecutionRules(settings)
    latest["action"] = latest.apply(lambda row: rules.suggested_action(row, portfolio_metrics["kill_switch_active"]), axis=1)

    explain = Explainer()
    latest["why"] = latest.apply(_build_why, axis=1)
    latest["why_short"] = latest.apply(explain.explain_row, axis=1)
    latest["what_changes"] = latest.apply(_what_changes, axis=1)
    latest["caveats"] = latest.apply(_caveats, axis=1)
    latest["invalidation_text"] = latest.apply(
        lambda row: f"Close below {row['invalidation_price']:.2f} (about {settings.risk.atr_multiple:.1f}x ATR below reference).",
        axis=1,
    )

    paper_actions = portfolio.apply_signals(latest.nlargest(5, "fused_confidence"), as_of)

    market_context = _build_market_context(latest)
    watchlist = _build_watchlist(latest)
    model_cards = {
        "factor": factor_model.model_card(),
        "deep": deep_model.fit_predict(features).metadata,
        "baseline": {"model": "hist_gradient_boosting_or_heuristic"},
        "governance": {
            "training_window": settings.lookback_days,
            "missingness": latest.isna().mean().sort_values(ascending=False).head(8).to_dict(),
            "last_update": as_of.isoformat(),
            "leakage_guard": "strict trailing features and shifted next-period targets",
            "drift_check": float(abs(latest["ret_5d"].mean() - features["ret_5d"].tail(len(latest)).mean())),
        },
    }
    return PipelineArtifacts(
        as_of=as_of,
        daily=daily,
        intraday=intraday,
        latest=latest,
        watchlist=watchlist,
        market_context=market_context,
        portfolio_metrics=portfolio_metrics,
        paper_actions=paper_actions,
        model_cards=model_cards,
    )


def _build_market_context(latest: pd.DataFrame) -> dict:
    def row_for(ticker: str) -> dict:
        row = latest[latest["ticker"] == ticker].head(1)
        if row.empty:
            return {}
        return row.iloc[0].to_dict()

    spy = row_for("SPY")
    qqq = row_for("QQQ")
    avg_risk = latest["vol_risk_score"].fillna(0.5).mean()
    risk_regime = "Elevated but tradeable" if avg_risk < 0.75 else "High risk"
    return {
        "spy_last": float(spy.get("close", 0)),
        "spy_ret_1d": float(spy.get("ret_1d", 0)),
        "spy_rv_5d": float(spy.get("rv_5d", 0)),
        "qqq_last": float(qqq.get("close", 0)),
        "qqq_ret_1d": float(qqq.get("ret_1d", 0)),
        "qqq_rv_5d": float(qqq.get("rv_5d", 0)),
        "risk_regime": risk_regime,
    }


def _build_watchlist(latest: pd.DataFrame) -> pd.DataFrame:
    ranked = latest[~latest["ticker"].isin({"SPY", "QQQ"})].copy()
    ranked["risk_adjusted"] = ranked["fused_confidence"] / (ranked["forecast_vol"].fillna(ranked["rv_20d"]).clip(lower=0.05))
    return ranked.sort_values(["risk_blocked", "risk_adjusted"], ascending=[True, False]).head(5)


def _build_why(row: pd.Series) -> str:
    catalysts = row.get("catalyst", "no fresh catalyst")
    narrative = row.get("narrative", "")
    return (
        f"5d realized vol {row.get('rv_5d', 0):.1%}, ATR {row.get('atr_pct', 0):.1%}, "
        f"liquidity ${row.get('avg_dollar_volume_20d', 0)/1e9:.2f}B, "
        f"factor {row.get('xsec_score', 0):+.2f}, time-series {row.get('ts_score', 0):+.2f}, "
        f"news catalyst {catalysts}. {narrative}"
    )


def _what_changes(row: pd.Series) -> str:
    return (
        f"Fused confidence below 0.50, adverse gap beyond {row.get('gap_pct', 0):+.1%}, "
        f"or negative catalyst escalation."
    )


def _caveats(row: pd.Series) -> str:
    caveats = []
    if row.get("risk_blocked", False):
        caveats.append("ticker is currently blocked for new entries")
    if pd.isna(row.get("intraday_ret_1h")):
        caveats.append("intraday data unavailable")
    if row.get("headline_count", 0) == 0:
        caveats.append("public news coverage sparse")
    return ", ".join(caveats) if caveats else "public-data signal stack only"

