from __future__ import annotations

from dataclasses import asdict, dataclass
import os

import numpy as np
import pandas as pd

from src.models.validation import evaluate_rank_predictions, walk_forward_splits

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
    validation: dict | None = None

    def fit_predict(self, features: pd.DataFrame) -> pd.DataFrame:
        df = features.sort_values(["ticker", "date"]).copy()
        df["target_up"] = (df.groupby("ticker")["ret_1d"].shift(-1) > 0).astype(float)
        df["target_next_1d"] = df.groupby("ticker")["ret_1d"].shift(-1)
        train = df.dropna(subset=FEATURES + ["target_up"]).copy()
        if HistGradientBoostingClassifier is None or len(train) < 100:
            df["baseline_score"] = self._heuristic(df)
            logits = np.clip(4 * df["baseline_score"].fillna(0), -20, 20)
            df["baseline_probability"] = 1 / (1 + np.exp(-logits))
            self.validation = asdict(
                evaluate_rank_predictions(df.dropna(subset=["target_next_1d"]), "baseline_score", "target_next_1d")
            )
            result = df[["date", "ticker", "baseline_score", "baseline_probability"]]
            result.attrs["validation"] = self.validation
            return result
        results = []
        dates = sorted(df["date"].dropna().unique().tolist())
        for train_dates, test_dates in walk_forward_splits(dates, min_train=40, step=5):
            train_split = df[df["date"].isin(train_dates)].dropna(subset=FEATURES + ["target_up"])
            test_split = df[df["date"].isin(test_dates)].copy()
            if train_split.empty or test_split.empty:
                continue
            X = train_split[FEATURES].fillna(0.0)
            y = train_split["target_up"]
            base = HistGradientBoostingClassifier(max_depth=4, learning_rate=0.05, max_iter=120)
            model = (
                CalibratedClassifierCV(base, method="isotonic", cv=3)
                if CalibratedClassifierCV is not None
                else base
            )
            model.fit(X, y)
            scores = model.predict_proba(test_split[FEATURES].fillna(0.0))[:, 1]
            out = test_split[["date", "ticker"]].copy()
            out["baseline_probability"] = scores
            out["baseline_score"] = (scores - 0.5) * 2
            results.append(out)
            self.model = model
        pred_df = pd.concat(results, ignore_index=True) if results else pd.DataFrame(columns=["date", "ticker", "baseline_score", "baseline_probability"])
        df = df.merge(pred_df, on=["date", "ticker"], how="left")
        missing = df["baseline_score"].isna()
        if missing.any():
            df.loc[missing, "baseline_score"] = self._heuristic(df.loc[missing])
            logits = np.clip(4 * df.loc[missing, "baseline_score"].fillna(0), -20, 20)
            df.loc[missing, "baseline_probability"] = 1 / (1 + np.exp(-logits))
        self.validation = asdict(
            evaluate_rank_predictions(df.dropna(subset=["target_next_1d"]), "baseline_score", "target_next_1d")
        )
        result = df[["date", "ticker", "baseline_score", "baseline_probability"]]
        result.attrs["validation"] = self.validation
        return result

    @staticmethod
    def _heuristic(df: pd.DataFrame) -> pd.Series:
        return (
            0.35 * df["ret_5d"].fillna(0)
            + 0.25 * df["ret_20d"].fillna(0)
            + 0.15 * df["intraday_ret_1h"].fillna(0)
            - 0.20 * df["rv_5d"].fillna(0)
            - 0.05 * df["gap_pct"].abs().fillna(0)
        )
