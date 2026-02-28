from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.config import AppConfig


@dataclass(slots=True)
class RiskEngine:
    settings: AppConfig

    def classify_risk(self, latest: pd.DataFrame) -> pd.DataFrame:
        df = latest.copy()
        intraday_vol_cutoff = df["intraday_rv"].quantile(self.settings.risk.risky_intraday_vol_percentile) if df["intraday_rv"].notna().any() else np.inf
        vol_z = self._zscore(df["intraday_volume"])
        df["risk_blocked"] = (
            (df["intraday_ret_1h"].fillna(0) <= self.settings.risk.risky_1h_return)
            | (df["gap_pct"].fillna(0) <= self.settings.risk.risky_gap_down)
            | ((vol_z > self.settings.risk.risky_volume_zscore) & (df["intraday_ret_1h"].fillna(0) < 0))
            | (df["intraday_rv"].fillna(0) >= intraday_vol_cutoff)
        )
        df["risk_label"] = np.where(df["risk_blocked"], "RISKY", df.get("risk_grade", "B"))
        df["invalidation_price"] = df["close"] - self.settings.risk.atr_multiple * df["atr"].fillna(df["close"] * 0.03)
        return df

    @staticmethod
    def _zscore(series: pd.Series) -> pd.Series:
        series = series.fillna(series.median())
        std = series.std(ddof=0)
        if std == 0 or pd.isna(std):
            return pd.Series(0.0, index=series.index)
        return (series - series.mean()) / std

