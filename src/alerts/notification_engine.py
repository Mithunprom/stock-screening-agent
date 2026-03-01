from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

import pandas as pd

from src.config import AppConfig
from src.state.store import SharedStateStore


@dataclass(slots=True)
class AlertPreference:
    ticker: str
    enabled: bool = True
    confidence_delta_threshold: float = 0.07
    predicted_move_threshold: float = 0.04
    risk_downgrade_alert: bool = True
    major_news_alert: bool = True
    cooldown_minutes: int = 90


class NotificationEngine:
    def __init__(self, settings: AppConfig) -> None:
        self.settings = settings
        self.store = SharedStateStore(settings)

    def tracked_preferences(self) -> dict[str, AlertPreference]:
        payload = self.store.read_json("frontend_preferences", {"watchlist": []})
        rows = payload.get("watchlist", [])
        prefs = {}
        for row in rows:
            prefs[str(row.get("ticker", "")).upper()] = AlertPreference(
                ticker=str(row.get("ticker", "")).upper(),
                enabled=bool(row.get("enabled", True)),
                confidence_delta_threshold=float(row.get("confidenceDeltaThreshold", 0.07)),
                predicted_move_threshold=float(row.get("predictedMoveThreshold", 0.04)),
                risk_downgrade_alert=bool(row.get("riskDowngradeAlert", True)),
                major_news_alert=bool(row.get("majorNewsAlert", True)),
                cooldown_minutes=int(row.get("cooldownMinutes", 90)),
            )
        return prefs

    def filter_digest_deltas(self, deltas: pd.DataFrame) -> pd.DataFrame:
        prefs = self.tracked_preferences()
        if not prefs or deltas.empty:
            return deltas
        rows = []
        for _, row in deltas.iterrows():
            pref = prefs.get(str(row.get("ticker", "")).upper())
            if pref is None or not pref.enabled:
                continue
            rows.append(row.to_dict())
        return pd.DataFrame(rows) if rows else deltas.head(0)

    def major_alerts(self, current: pd.DataFrame, previous: pd.DataFrame, as_of: datetime) -> pd.DataFrame:
        prefs = self.tracked_preferences()
        if not prefs or current.empty:
            return current.head(0)
        prev_lookup = previous.set_index("ticker") if not previous.empty else pd.DataFrame()
        alert_log = self.store.read_json("alert_log", {"events": []})
        log_rows = alert_log.get("events", [])
        rows: list[dict] = []
        for _, row in current.iterrows():
            ticker = str(row.get("ticker", "")).upper()
            pref = prefs.get(ticker)
            if pref is None or not pref.enabled:
                continue
            prev = prev_lookup.loc[ticker] if not prev_lookup.empty and ticker in prev_lookup.index else None
            confidence_delta = abs(float(row.get("fused_confidence", 0)) - float(prev.get("fused_confidence", 0) if prev is not None else 0))
            predicted_move = abs(float(row.get("ts_score", 0)))
            major_news = (
                pref.major_news_alert
                and float(row.get("event_risk_score", 0) or 0) >= 0.65
                and float(row.get("catalyst_confidence", 0) or 0) >= 0.5
            )
            confidence_break = confidence_delta >= pref.confidence_delta_threshold
            predicted_break = predicted_move >= pref.predicted_move_threshold
            risk_break = pref.risk_downgrade_alert and str(row.get("risk_label", "")) == "RISKY"
            if not (major_news or confidence_break or predicted_break or risk_break):
                continue
            reason_parts = []
            if major_news:
                reason_parts.append(f"major catalyst: {row.get('catalyst', 'news')}")
            if confidence_break:
                reason_parts.append(f"confidence delta {confidence_delta:.0%}")
            if predicted_break:
                reason_parts.append(f"predicted move proxy {predicted_move:.0%}")
            if risk_break:
                reason_parts.append("risk downgrade")
            signature = f"{ticker}|{row.get('catalyst','')}|{row.get('risk_label','')}|{round(confidence_delta,3)}|{round(predicted_move,3)}"
            if self._within_cooldown(log_rows, ticker, signature, as_of, pref.cooldown_minutes):
                continue
            payload = row.to_dict()
            payload["alert_reason"] = ", ".join(reason_parts)
            rows.append(payload)
            log_rows.append({"ticker": ticker, "signature": signature, "sent_at": as_of.isoformat()})
        self.store.write_json("alert_log", {"events": log_rows[-500:]})
        return pd.DataFrame(rows)

    @staticmethod
    def _within_cooldown(log_rows: list[dict], ticker: str, signature: str, as_of: datetime, cooldown_minutes: int) -> bool:
        for row in reversed(log_rows):
            if row.get("ticker") != ticker:
                continue
            sent_at = datetime.fromisoformat(str(row.get("sent_at")))
            if as_of - sent_at > timedelta(minutes=cooldown_minutes):
                return False
            if row.get("signature") == signature:
                return True
        return False
