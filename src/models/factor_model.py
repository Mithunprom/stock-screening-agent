from __future__ import annotations

from dataclasses import dataclass
from dataclasses import asdict

import numpy as np
import pandas as pd

from src.models.validation import ValidationResult, evaluate_rank_predictions, walk_forward_splits


FACTOR_COLUMNS = [
    "ret_1d",
    "ret_5d",
    "ret_20d",
    "reversal_5d",
    "rv_5d",
    "rv_20d",
    "avg_dollar_volume_20d",
    "beta_spy",
    "beta_qqq",
    "range_pct",
    "gap_pct",
    "intraday_ret_1h",
    "sector_relative_momentum_5d",
]


@dataclass(slots=True)
class FactorModel:
    weights: dict[str, float] | None = None
    validation: ValidationResult | None = None

    def fit_predict(self, features: pd.DataFrame) -> pd.DataFrame:
        df = features.sort_values(["date", "ticker"]).copy()
        df["target_next_1d"] = df.groupby("ticker")["ret_1d"].shift(-1)
        unique_dates = sorted(df["date"].dropna().unique().tolist())
        predictions = []
        weight_history: list[dict[str, float]] = []
        for train_dates, test_dates in walk_forward_splits(unique_dates, min_train=40, step=5):
            train = df[df["date"].isin(train_dates)].dropna(subset=["target_next_1d"])
            test = df[df["date"].isin(test_dates)].copy()
            if train.empty or test.empty:
                continue
            weights = self._fit_weights(train)
            weight_history.append(weights)
            test["xsec_score_raw"] = self._score_frame(test, weights)
            test["xsec_score"] = self._neutralize(test)
            predictions.append(test[["date", "ticker", "xsec_score_raw", "xsec_score"]])
        self.weights = weight_history[-1] if weight_history else self._fit_weights(df.dropna(subset=["target_next_1d"]))
        pred_df = pd.concat(predictions, ignore_index=True) if predictions else pd.DataFrame(columns=["date", "ticker", "xsec_score_raw", "xsec_score"])
        df = df.merge(pred_df, on=["date", "ticker"], how="left", suffixes=("", "_pred"))
        missing = df["xsec_score"].isna()
        if missing.any():
            df.loc[missing, "xsec_score_raw"] = self._score_frame(df.loc[missing], self.weights or {})
            df.loc[missing, "xsec_score"] = self._neutralize(df.loc[missing])
        self.validation = evaluate_rank_predictions(
            df.dropna(subset=["target_next_1d"]),
            "xsec_score",
            "target_next_1d",
        )
        return df

    @staticmethod
    def _fit_weights(train: pd.DataFrame) -> dict[str, float]:
        corr_weights = {}
        for col in FACTOR_COLUMNS:
            if col in train:
                corr = train[col].corr(train["target_next_1d"], method="spearman")
                corr_weights[col] = 0.0 if pd.isna(corr) else float(corr)
        return corr_weights

    @staticmethod
    def _score_frame(df: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
        score = pd.Series(0.0, index=df.index)
        for col in FACTOR_COLUMNS:
            score = score + df.get(col, 0).fillna(0) * weights.get(col, 0.0)
        return score

    @staticmethod
    def _neutralize(df: pd.DataFrame) -> pd.Series:
        residuals = []
        for _, chunk in df.groupby("date"):
            beta_spy = chunk["beta_spy"]
            beta_qqq = chunk["beta_qqq"]
            x1 = beta_spy.fillna(beta_spy.median() if pd.notna(beta_spy.median()) else 0.0).to_numpy(dtype=float)
            x2 = beta_qqq.fillna(beta_qqq.median() if pd.notna(beta_qqq.median()) else 0.0).to_numpy(dtype=float)
            y = chunk["xsec_score_raw"].fillna(0.0).to_numpy(dtype=float)
            sector_dummies = pd.get_dummies(chunk["sector"].fillna("Other"), dtype=float)
            X = np.column_stack([np.ones(len(chunk)), x1, x2, sector_dummies.to_numpy()])
            X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
            y = np.nan_to_num(y, nan=0.0, posinf=0.0, neginf=0.0)
            try:
                coef = np.linalg.pinv(X) @ y
            except np.linalg.LinAlgError:
                coef = np.zeros(X.shape[1], dtype=float)
            residual = y - X @ coef
            residuals.extend(residual.tolist())
        return pd.Series(residuals, index=df.index)

    def model_card(self) -> dict:
        return {
            "model": "cross_sectional_factor",
            "features": FACTOR_COLUMNS,
            "weights": self.weights or {},
            "sector_neutralized": True,
            "validation": asdict(self.validation) if self.validation else {},
        }
