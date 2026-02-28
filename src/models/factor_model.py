from __future__ import annotations

from dataclasses import dataclass
from dataclasses import asdict

import numpy as np
import pandas as pd

from src.models.validation import ValidationResult, evaluate_rank_predictions


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
]


@dataclass(slots=True)
class FactorModel:
    weights: dict[str, float] | None = None
    validation: ValidationResult | None = None

    def fit_predict(self, features: pd.DataFrame) -> pd.DataFrame:
        df = features.sort_values(["date", "ticker"]).copy()
        df["target_next_1d"] = df.groupby("ticker")["ret_1d"].shift(-1)
        clean = df.dropna(subset=["target_next_1d"])
        corr_weights = {}
        for col in FACTOR_COLUMNS:
            if col in clean:
                corr = clean[col].corr(clean["target_next_1d"], method="spearman")
                corr_weights[col] = 0.0 if pd.isna(corr) else float(corr)
        self.weights = corr_weights
        df["xsec_score_raw"] = sum(df.get(col, 0).fillna(0) * corr_weights.get(col, 0.0) for col in FACTOR_COLUMNS)
        df["xsec_score"] = self._neutralize(df)
        self.validation = evaluate_rank_predictions(df.dropna(subset=["target_next_1d"]), "xsec_score", "target_next_1d")
        return df

    @staticmethod
    def _neutralize(df: pd.DataFrame) -> pd.Series:
        residuals = []
        for _, chunk in df.groupby("date"):
            beta_spy = chunk["beta_spy"]
            beta_qqq = chunk["beta_qqq"]
            x1 = beta_spy.fillna(beta_spy.median() if pd.notna(beta_spy.median()) else 0.0).to_numpy(dtype=float)
            x2 = beta_qqq.fillna(beta_qqq.median() if pd.notna(beta_qqq.median()) else 0.0).to_numpy(dtype=float)
            y = chunk["xsec_score_raw"].fillna(0.0).to_numpy(dtype=float)
            X = np.column_stack([np.ones(len(chunk)), x1, x2])
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
            "validation": asdict(self.validation) if self.validation else {},
        }
