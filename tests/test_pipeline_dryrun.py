from src.pipelines.daily_job import run as run_daily
from src.pipelines.hourly_job import run as run_hourly


def test_daily_job_dry_run_outputs_report() -> None:
    subject, body = run_daily(dry_run=True)
    assert "Daily Opportunity + Catalyst Screen" in subject
    assert "Top 20 Opportunity Screen" in body
    assert "Watchlist Highlights" in body


def test_hourly_job_force_dry_run_outputs_report() -> None:
    result = run_hourly(dry_run=True, force=True)
    assert result is not None
    subject, body = result
    assert "Hourly Update" in subject
    assert "Material Changes" in body
