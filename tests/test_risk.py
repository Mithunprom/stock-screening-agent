from datetime import datetime

import pandas as pd

from src.config import get_settings
from src.portfolio.paper_portfolio import PaperPortfolio, Position
from src.portfolio.risk import RiskEngine


def test_risky_ticker_is_blocked() -> None:
    settings = get_settings()
    frame = pd.DataFrame(
        [
            {
                "ticker": "ABC",
                "close": 10.0,
                "gap_pct": -0.09,
                "intraday_ret_1h": -0.08,
                "intraday_volume": 10,
                "intraday_rv": 1.0,
                "atr": 0.5,
                "risk_grade": "B",
            }
        ]
    )
    result = RiskEngine(settings).classify_risk(frame)
    assert bool(result.iloc[0]["risk_blocked"])


def test_kill_switch_triggers_on_drawdown(tmp_path) -> None:
    settings = get_settings()
    settings.state_dir = tmp_path
    portfolio = PaperPortfolio(settings)
    portfolio.state.positions["ABC"] = Position(ticker="ABC", quantity=10, avg_entry=10.0)
    portfolio.state.cash = 900.0
    first = portfolio.mark_to_market({"ABC": 10.0}, datetime(2026, 2, 27, 10, 0))
    assert not first["kill_switch_active"]
    second = portfolio.mark_to_market({"ABC": 0.0}, datetime(2026, 2, 27, 12, 0))
    assert second["kill_switch_active"]
