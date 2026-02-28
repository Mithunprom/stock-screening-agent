from __future__ import annotations

import argparse

from src.alerts.emailer import Emailer
from src.alerts.templates import render_daily_email
from src.config import get_settings
from src.pipelines.common import build_pipeline_artifacts, persist_tracking_snapshot


def run(dry_run: bool = False) -> tuple[str, str]:
    settings = get_settings()
    artifacts = build_pipeline_artifacts(settings)
    persist_tracking_snapshot(settings, artifacts)
    screen = (
        artifacts.latest[~artifacts.latest["ticker"].isin({"SPY", "QQQ"})]
        .sort_values(["risk_blocked", "opportunity_score", "headline_count"], ascending=[True, False, False])
        .head(settings.universe.top_n_volatility)
        .copy()
    )
    subject, body = render_daily_email(artifacts.as_of, artifacts.market_context, screen, artifacts.watchlist)
    Emailer(settings).send(subject, body, dry_run=dry_run)
    return subject, body


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
