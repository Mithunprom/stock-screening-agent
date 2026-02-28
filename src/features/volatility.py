from __future__ import annotations

import numpy as np
import pandas as pd


def realized_volatility(returns: pd.Series, window: int = 5, annualize: bool = True) -> pd.Series:
    scale = np.sqrt(252) if annualize else 1.0
    return returns.rolling(window).std(ddof=0) * scale


def true_range(frame: pd.DataFrame) -> pd.Series:
    prev_close = frame.groupby("ticker")["close"].shift(1)
    ranges = pd.concat(
        [
            (frame["high"] - frame["low"]).abs(),
            (frame["high"] - prev_close).abs(),
            (frame["low"] - prev_close).abs(),
        ],
        axis=1,
    )
    return ranges.max(axis=1)


def average_true_range(frame: pd.DataFrame, window: int = 14) -> pd.Series:
    tr = true_range(frame)
    return tr.groupby(frame["ticker"]).transform(lambda x: x.rolling(window).mean())

