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
        catalyst_component = (
            0.45 * df["event_score"].fillna(0)
            + 0.35 * df["catalyst_confidence"].fillna(0)
            - 0.20 * df["event_risk_score"].fillna(0)
        )
        liquidity_component = np.log1p(df["avg_dollar_volume_20d"].fillna(0)).replace([np.inf, -np.inf], 0)
        liquidity_component = liquidity_component / max(float(liquidity_component.max() or 1.0), 1.0)
        risk_blocked = df["risk_blocked"].fillna(False).astype(float) if "risk_blocked" in df.columns else 0.0
        df["opportunity_score"] = (
            0.50 * df["fused_confidence"].fillna(0)
            + 0.20 * catalyst_component
            + 0.15 * df["baseline_probability"].fillna(0)
            + 0.10 * liquidity_component
            - 0.20 * df["vol_risk_score"].fillna(0)
            - 0.15 * risk_blocked
        )
        df["conviction_label"] = pd.cut(
            df["opportunity_score"].fillna(0),
            bins=[-np.inf, 0.15, 0.35, 0.60, np.inf],
            labels=["Low", "Developing", "Strong", "High"],
        ).astype(str)
        df["risk_grade"] = pd.cut(
            df["vol_risk_score"].fillna(0.5),
            bins=[-np.inf, 0.35, 0.55, 0.75, np.inf],
            labels=["A", "B", "C", "RISKY"],
        ).astype(str)
        return df
