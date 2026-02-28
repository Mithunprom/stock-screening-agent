from __future__ import annotations

from dataclasses import dataclass
import os

import numpy as np
import pandas as pd

SKLEARN_ENABLED = os.getenv("ENABLE_SKLEARN_BASELINE", "0").lower() in {"1", "true", "yes"}

try:
    if not SKLEARN_ENABLED:
        raise ImportError("sklearn boosted baseline disabled by default for stable local dry-runs")
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.ensemble import HistGradientBoostingClassifier
except Exception:  # pragma: no cover
    CalibratedClassifierCV = None
    HistGradientBoostingClassifier = None


FEATURES = [
    "ret_1d",
    "ret_5d",
    "ret_20d",
    "rv_5d",
    "rv_20d",
    "avg_dollar_volume_20d",
    "beta_spy",
    "gap_pct",
    "atr_pct",
    "intraday_ret_1h",
]


@dataclass(slots=True)
class BaselineModel:
    model: object | None = None

    def fit_predict(self, features: pd.DataFrame) -> pd.DataFrame:
        df = features.sort_values(["ticker", "date"]).copy()
        df["target_up"] = (df.groupby("ticker")["ret_1d"].shift(-1) > 0).astype(float)
        train = df.dropna(subset=FEATURES + ["target_up"]).copy()
        if HistGradientBoostingClassifier is None or len(train) < 100:
            df["baseline_score"] = self._heuristic(df)
            df["baseline_probability"] = 1 / (1 + np.exp(-4 * df["baseline_score"].fillna(0)))
            return df[["date", "ticker", "baseline_score", "baseline_probability"]]
        X = train[FEATURES].fillna(0.0)
        y = train["target_up"]
        base = HistGradientBoostingClassifier(max_depth=4, learning_rate=0.05, max_iter=120)
        self.model = (
            CalibratedClassifierCV(base, method="isotonic", cv=3)
            if CalibratedClassifierCV is not None
            else base
        )
        self.model.fit(X, y)
        scores = self.model.predict_proba(df[FEATURES].fillna(0.0))[:, 1]
        df["baseline_probability"] = scores
        df["baseline_score"] = (scores - 0.5) * 2
        return df[["date", "ticker", "baseline_score", "baseline_probability"]]

    @staticmethod
    def _heuristic(df: pd.DataFrame) -> pd.Series:
        return (
            0.35 * df["ret_5d"].fillna(0)
            + 0.25 * df["ret_20d"].fillna(0)
            + 0.15 * df["intraday_ret_1h"].fillna(0)
            - 0.20 * df["rv_5d"].fillna(0)
            - 0.05 * df["gap_pct"].abs().fillna(0)
        )
