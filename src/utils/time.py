from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def now_local(tz_name: str) -> datetime:
    return now_utc().astimezone(ZoneInfo(tz_name))


def format_date(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


def format_hour_et(dt: datetime) -> str:
    return dt.astimezone(ZoneInfo("America/New_York")).strftime("%H:00 ET")

