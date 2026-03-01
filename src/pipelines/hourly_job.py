from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.alerts.emailer import Emailer
from src.alerts.notification_engine import NotificationEngine
from src.alerts.templates import render_event_alert_email, render_hourly_email
from src.config import get_settings
from src.data.calendar import market_session_status
from src.pipelines.common import build_pipeline_artifacts, persist_tracking_snapshot
from src.state.store import SharedStateStore
from src.utils.io import read_json, write_json


def run(dry_run: bool = False, force: bool = False) -> tuple[str, str] | None:
    settings = get_settings()
    artifacts = build_pipeline_artifacts(settings)
    session = market_session_status(artifacts.as_of)
    if not force and not session.is_open:
        return None

    store = SharedStateStore(settings)
    state_path = settings.state_dir / "hourly_state.json"
    previous = store.read_json("hourly_state", {"rows": []})
    prev_df = pd.DataFrame(previous.get("rows", []))
    current = artifacts.latest[["ticker", "fused_confidence", "risk_label", "action", "why_short", "invalidation_text"]].copy()
    for optional_col in ["catalyst", "event_risk_score", "catalyst_confidence", "ts_score"]:
        if optional_col in artifacts.latest.columns:
            current[optional_col] = artifacts.latest[optional_col]
    current["change_reason"] = current["why_short"]
    if prev_df.empty:
        deltas = current.head(10)
    else:
        merged = current.merge(prev_df, on="ticker", how="left", suffixes=("", "_prev"))
        deltas = merged[
            (merged["fused_confidence_prev"].isna())
            | ((merged["fused_confidence"] - merged["fused_confidence_prev"]).abs() >= 0.05)
            | (merged["risk_label"] != merged["risk_label_prev"])
            | (merged["action"] != merged["action_prev"])
        ][current.columns]
    payload = {"rows": current.to_dict(orient="records"), "deltas": deltas.to_dict(orient="records"), "as_of": artifacts.as_of.isoformat()}
    write_json(state_path, payload)
    store.write_json("hourly_state", payload)
    persist_tracking_snapshot(settings, artifacts)
    notifier = NotificationEngine(settings)
    digest_deltas = notifier.filter_digest_deltas(deltas.sort_values("fused_confidence", ascending=False))
    subject, body = render_hourly_email(artifacts.as_of, digest_deltas, artifacts.portfolio_metrics)
    Emailer(settings).send(subject, body, dry_run=dry_run)
    event_alerts = notifier.major_alerts(current, prev_df, artifacts.as_of)
    if not event_alerts.empty:
        event_subject, event_body = render_event_alert_email(artifacts.as_of, event_alerts.sort_values("fused_confidence", ascending=False))
        Emailer(settings).send(event_subject, event_body, dry_run=dry_run)
    return subject, body


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    run(dry_run=args.dry_run, force=args.force)


if __name__ == "__main__":
    main()
