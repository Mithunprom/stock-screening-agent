from __future__ import annotations

from typing import Any

from src.api_service.sample_data import sample_candles, sample_dashboard, sample_preferences, sample_quote
from src.api_service.state import read_shared_json


class ResearchApiService:
    def dashboard(self) -> dict[str, Any]:
        latest = read_shared_json("latest_snapshot", None)
        if not latest:
            return sample_dashboard()
        payload = sample_dashboard()
        payload["as_of"] = latest.get("as_of", payload["as_of"])
        payload["market_context"] = latest.get("market_context", payload["market_context"])
        payload["recommendations"] = self._merge_rows(latest.get("recommendations", []), payload["recommendations"])
        payload["watchlist"] = self._merge_rows(latest.get("watchlist", []), payload["watchlist"])
        payload["positions"] = latest.get("positions", payload["positions"])
        payload["paper_actions"] = latest.get("paper_actions", payload["paper_actions"])
        payload["portfolio_state"] = {**payload["portfolio_state"], **latest.get("portfolio_state", {})}
        payload["news"] = self.latest_news()
        payload["data_status"] = {
            "latencyMs": 420,
            "level": "green",
            "feed": "fastapi-shared-state",
            "note": "FastAPI backend serving cached shared-state research output.",
        }
        return payload

    def quote(self, ticker: str) -> dict[str, Any]:
        dashboard = self.dashboard()
        row = next((item for item in dashboard["recommendations"] if item["ticker"] == ticker), None)
        if row is None:
            return sample_quote(ticker)
        return {
            "ticker": ticker,
            "price": row["close"],
            "changePct": row.get("ts_score", 0) / 10,
            "updatedAt": dashboard["as_of"],
            "source": dashboard["data_status"]["feed"],
        }

    def candles(self, ticker: str, range_name: str, interval: str) -> dict[str, Any]:
        return {
            "ticker": ticker,
            "range": range_name,
            "interval": interval if interval in {"1m", "5m", "15m", "1h", "1d"} else "1h",
            "note": "Deterministic sample candles when live intraday feed is unavailable.",
            "candles": sample_candles(ticker, range_name, interval),
        }

    def top_volatile(self, limit: int = 20) -> dict[str, Any]:
        rows = sorted(self.dashboard()["recommendations"], key=lambda row: row.get("rv_5d", 0), reverse=True)[:limit]
        return {"window": "5d", "rows": rows}

    def latest_news(self, tickers: list[str] | None = None) -> list[dict[str, Any]]:
        dashboard = self.dashboard() if False else None
        if dashboard is None:
            dashboard = sample_dashboard()
        feed = dashboard.get("news", [])
        if not tickers:
            return feed
        tickers_set = set(tickers)
        return [item for item in feed if item.get("ticker") in tickers_set]

    def signal_summary(self, ticker: str) -> dict[str, Any]:
        dashboard = self.dashboard()
        row = next((item for item in dashboard["recommendations"] if item["ticker"] == ticker), None)
        if row is None:
            return {
                "ticker": ticker,
                "fused": 0.5,
                "action": "WATCH",
                "riskLabel": "OK",
                "invalidationPrice": 100,
                "volatilityRegime": "Contained",
                "signals": {"factor": 0.2, "timeSeries": 0.1, "news": 0.2, "volatility": 0.6},
                "topDrivers": [{"label": "Sample data", "value": 0.3}],
                "whyNow": ["Sample-mode summary."],
                "modelFreshness": dashboard["model_freshness"]["factor"],
            }
        return {
            "ticker": ticker,
            "fused": row["fused_confidence"],
            "action": row["action"],
            "riskLabel": row["risk_label"],
            "invalidationPrice": row["invalidation_price"],
            "volatilityRegime": "Hot" if row.get("vol_risk_score", 0) > 0.7 else "Active" if row.get("vol_risk_score", 0) > 0.45 else "Contained",
            "signals": {
                "factor": row.get("xsec_score", 0),
                "timeSeries": row.get("ts_score", 0),
                "news": row.get("event_risk_score", 0),
                "volatility": 1 - row.get("vol_risk_score", 0),
            },
            "topDrivers": [
                {"label": "Factor spread", "value": row.get("xsec_score", 0)},
                {"label": "Time-series edge", "value": row.get("ts_score", 0)},
                {"label": "News impact", "value": row.get("event_risk_score", 0)},
                {"label": "Volatility penalty", "value": -row.get("vol_risk_score", 0)},
            ],
            "whyNow": [
                row.get("why_short", "Price action and factor breadth are supportive."),
                f"Invalidation sits near {row.get('invalidation_price', 0):.2f} with {row.get('hold_horizon', '1-5 days')} horizon.",
                f"News catalyst: {row.get('catalyst', 'company news')}.",
            ],
            "modelFreshness": dashboard["model_freshness"]["factor"],
        }

    def portfolio_state(self) -> dict[str, Any]:
        dashboard = self.dashboard()
        return {"positions": dashboard["positions"], "state": dashboard["portfolio_state"]}

    def preferences(self) -> dict[str, Any]:
        return read_shared_json("frontend_preferences", sample_preferences())

    def save_preferences(self, payload: dict[str, Any]) -> dict[str, Any]:
        from src.state.store import SharedStateStore
        from src.config import get_settings

        SharedStateStore(get_settings()).write_json("frontend_preferences", payload)
        return payload

    def update_watchlist(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        prefs = self.preferences()
        next_rows = [row for row in prefs.get("watchlist", []) if row.get("ticker") != payload.get("ticker")]
        next_rows.insert(0, payload)
        prefs["watchlist"] = next_rows
        self.save_preferences(prefs)
        return next_rows

    @staticmethod
    def _merge_rows(rows: list[dict[str, Any]], sample_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        merged = []
        for idx, row in enumerate(rows):
            sample = sample_rows[idx % len(sample_rows)] if sample_rows else {}
            merged.append({**sample, **row})
        return merged or sample_rows
