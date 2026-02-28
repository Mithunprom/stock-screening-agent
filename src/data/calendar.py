from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from src.utils.logging import get_logger

logger = get_logger(__name__)

try:
    import pandas_market_calendars as mcal  # type: ignore
except Exception:  # pragma: no cover
    mcal = None


FALLBACK_HOLIDAYS_2026 = {
    date(2026, 1, 1),
    date(2026, 1, 19),
    date(2026, 2, 16),
    date(2026, 4, 3),
    date(2026, 5, 25),
    date(2026, 6, 19),
    date(2026, 7, 3),
    date(2026, 9, 7),
    date(2026, 11, 26),
    date(2026, 12, 25),
}


@dataclass(slots=True)
class MarketSession:
    is_open: bool
    reason: str


def is_trading_day(day: date) -> bool:
    if mcal is not None:
        cal = mcal.get_calendar("NYSE")
        sched = cal.schedule(start_date=day, end_date=day)
        return not sched.empty
    return day.weekday() < 5 and day not in FALLBACK_HOLIDAYS_2026


def market_session_status(ts: datetime) -> MarketSession:
    et = ts.astimezone(ZoneInfo("America/New_York"))
    if not is_trading_day(et.date()):
        return MarketSession(False, "Weekend or NYSE holiday")
    market_open = datetime.combine(et.date(), time(9, 30), tzinfo=et.tzinfo)
    market_close = datetime.combine(et.date(), time(16, 0), tzinfo=et.tzinfo)
    if et < market_open:
        return MarketSession(False, "Pre-market")
    if et > market_close:
        return MarketSession(False, "Post-market")
    return MarketSession(True, "Open")


def previous_trading_day(day: date) -> date:
    cursor = day - timedelta(days=1)
    while not is_trading_day(cursor):
        cursor -= timedelta(days=1)
    return cursor

