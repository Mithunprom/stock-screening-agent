from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.models.validation import ValidationResult


@dataclass(slots=True)
class FusionModel:
    def fuse(
        self,
        latest: pd.DataFrame,
        factor_validation: ValidationResult | None = None,
    ) -> pd.DataFrame:
        df = latest.copy()
        regime_boost = np.where(df["rv_5d"].fillna(0) > df["rv_20d"].fillna(df["rv_5d"]), 0.9, 1.0)
        xsec_weight = 0.30 if factor_validation is None else max(0.15, min(0.45, 0.25 + factor_validation.ic))
        ts_weight = 0.25
        base_weight = 0.25
        news_weight = 0.10
        vol_weight = 0.10
        df["fused_score"] = regime_boost * (
            xsec_weight * df["xsec_score"].fillna(0)
            + ts_weight * (df["ts_score"].fillna(0) / df["ts_uncertainty"].replace(0, np.nan).fillna(1.0))
            + base_weight * df["baseline_score"].fillna(0)
            + news_weight * df["event_score"].fillna(0)
            - vol_weight * df["vol_risk_score"].fillna(0)
        )
        logits = np.clip(3 * df["fused_score"].fillna(0), -20, 20)
        df["fused_confidence"] = 1 / (1 + np.exp(-logits))
        df["risk_grade"] = pd.cut(
            df["vol_risk_score"].fillna(0.5),
            bins=[-np.inf, 0.35, 0.55, 0.75, np.inf],
            labels=["A", "B", "C", "RISKY"],
        ).astype(str)
        return df
