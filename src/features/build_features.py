from __future__ import annotations

import numpy as np
import pandas as pd

from src.features.volatility import average_true_range, realized_volatility


def build_feature_frame(daily: pd.DataFrame, intraday: pd.DataFrame | None = None) -> pd.DataFrame:
    df = daily.sort_values(["ticker", "date"]).copy()
    df["ret_1d"] = df.groupby("ticker")["close"].pct_change(1)
    df["ret_5d"] = df.groupby("ticker")["close"].pct_change(5)
    df["ret_20d"] = df.groupby("ticker")["close"].pct_change(20)
    df["reversal_5d"] = -df["ret_5d"]
    df["gap_pct"] = (df["open"] / df.groupby("ticker")["close"].shift(1)) - 1.0
    df["dollar_volume"] = df["close"] * df["volume"]
    df["avg_dollar_volume_20d"] = df.groupby("ticker")["dollar_volume"].transform(lambda x: x.rolling(20).mean())
    df["rv_5d"] = df.groupby("ticker")["ret_1d"].transform(lambda x: realized_volatility(x, 5))
    df["rv_20d"] = df.groupby("ticker")["ret_1d"].transform(lambda x: realized_volatility(x, 20))
    df["atr"] = average_true_range(df, 14)
    df["atr_pct"] = df["atr"] / df["close"]
    df["range_pct"] = (df["high"] - df["low"]) / df["close"]

    spy_returns = df[df["ticker"] == "SPY"][["date", "ret_1d"]].rename(columns={"ret_1d": "spy_ret_1d"})
    qqq_returns = df[df["ticker"] == "QQQ"][["date", "ret_1d"]].rename(columns={"ret_1d": "qqq_ret_1d"})
    df = df.merge(spy_returns, on="date", how="left").merge(qqq_returns, on="date", how="left")

    def rolling_beta(asset: pd.Series, benchmark: pd.Series, window: int = 20) -> pd.Series:
        cov = asset.rolling(window).cov(benchmark)
        var = benchmark.rolling(window).var()
        return cov / var.replace(0, np.nan)

    df["beta_spy"] = df.groupby("ticker", group_keys=False).apply(
        lambda x: rolling_beta(x["ret_1d"], x["spy_ret_1d"])
    ).reset_index(level=0, drop=True)
    df["beta_qqq"] = df.groupby("ticker", group_keys=False).apply(
        lambda x: rolling_beta(x["ret_1d"], x["qqq_ret_1d"])
    ).reset_index(level=0, drop=True)

    if intraday is not None and not intraday.empty:
        intraday = intraday.sort_values(["ticker", "date"]).copy()
        intraday["ret_1h"] = intraday.groupby("ticker")["close"].pct_change(1)
        intraday_summary = intraday.groupby("ticker").agg(
            intraday_ret_1h=("ret_1h", "last"),
            intraday_rv=("ret_1h", lambda x: x.tail(6).std(ddof=0) * np.sqrt(6 * 252)),
            intraday_volume=("volume", "mean"),
        )
        df = df.merge(intraday_summary, on="ticker", how="left")
    else:
        df["intraday_ret_1h"] = np.nan
        df["intraday_rv"] = np.nan
        df["intraday_volume"] = np.nan

    return df.replace([np.inf, -np.inf], np.nan)

