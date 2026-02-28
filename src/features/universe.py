from __future__ import annotations

import pandas as pd

from src.config import AppConfig


def filter_universe(daily: pd.DataFrame, settings: AppConfig) -> list[str]:
    latest = daily.sort_values("date").groupby("ticker").tail(1)
    liquidity = daily.assign(dollar_volume=daily["close"] * daily["volume"]).groupby("ticker")["dollar_volume"].tail(20)
    avg_dollar = daily.assign(dollar_volume=daily["close"] * daily["volume"]).groupby("ticker")["dollar_volume"].mean()
    counts = daily.groupby("ticker").size()
    eligible = latest["ticker"][
        (latest["close"] >= settings.universe.min_price)
        & (latest["ticker"].map(avg_dollar) >= settings.universe.min_avg_dollar_volume)
        & (latest["ticker"].map(counts) >= settings.universe.min_listing_days)
    ]
    return sorted(set(eligible.tolist()) | {"SPY", "QQQ"})

