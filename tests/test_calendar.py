from datetime import date, datetime
from zoneinfo import ZoneInfo

from src.data.calendar import is_trading_day, market_session_status


def test_weekend_is_not_trading_day() -> None:
    assert not is_trading_day(date(2026, 2, 28))


def test_market_hours_status_open() -> None:
    ts = datetime(2026, 2, 27, 10, 0, tzinfo=ZoneInfo("America/New_York"))
    status = market_session_status(ts)
    assert status.is_open

