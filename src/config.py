from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass(slots=True)
class RiskConfig:
    daily_drawdown_kill_switch: float = 0.10
    max_position_pct: float = float(os.getenv("SCREENER_MAX_POS_PCT", "0.20"))
    max_gross_exposure_pct: float = float(os.getenv("SCREENER_MAX_GROSS_PCT", "0.60"))
    atr_multiple: float = 2.0
    risky_1h_return: float = -0.06
    risky_gap_down: float = -0.08
    risky_volume_zscore: float = 3.0
    risky_intraday_vol_percentile: float = 0.95


@dataclass(slots=True)
class UniverseConfig:
    tickers: List[str] = field(
        default_factory=lambda: [
            "AAPL",
            "MSFT",
            "NVDA",
            "AMZN",
            "META",
            "TSLA",
            "AMD",
            "SMCI",
            "PLTR",
            "NFLX",
            "AVGO",
            "JPM",
            "BAC",
            "XOM",
            "CVX",
            "LLY",
            "UNH",
            "COIN",
            "SHOP",
            "UBER",
            "SPY",
            "QQQ",
            "IWM",
            "XLF",
            "XLK",
            "XLE",
            "XLY",
            "XLV",
        ]
    )
    min_price: float = float(os.getenv("SCREENER_MIN_PRICE", "2"))
    min_avg_dollar_volume: float = float(os.getenv("SCREENER_MIN_AVG_DOLLAR_VOLUME", "5000000"))
    min_listing_days: int = int(os.getenv("SCREENER_MIN_LISTING_DAYS", "30"))
    top_n_volatility: int = 20


@dataclass(slots=True)
class EmailConfig:
    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_pass: str = os.getenv("SMTP_PASS", "")
    email_from: str = os.getenv("EMAIL_FROM", "")
    email_to: List[str] = field(
        default_factory=lambda: [x.strip() for x in os.getenv("EMAIL_TO", "").split(",") if x.strip()]
    )
    dry_run_default: bool = os.getenv("EMAIL_DRY_RUN", "false").lower() == "true"


@dataclass(slots=True)
class AppConfig:
    timezone: str = os.getenv("SCREENER_TIMEZONE", "America/Los_Angeles")
    state_dir: Path = Path(os.getenv("SCREENER_STATE_DIR", ".state"))
    cache_dir: Path = Path(os.getenv("SCREENER_CACHE_DIR", ".cache"))
    market_proxy: str = "SPY"
    tech_proxy: str = "QQQ"
    transaction_cost_bps: float = 10.0
    slippage_bps: float = 5.0
    starting_cash: float = 1000.0
    lookback_days: int = 90
    intraday_interval: str = "60m"
    risk: RiskConfig = field(default_factory=RiskConfig)
    universe: UniverseConfig = field(default_factory=UniverseConfig)
    email: EmailConfig = field(default_factory=EmailConfig)

    def ensure_dirs(self) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)


def get_settings() -> AppConfig:
    settings = AppConfig()
    settings.ensure_dirs()
    return settings

