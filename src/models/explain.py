from __future__ import annotations

from dataclasses import dataclass
import os

import pandas as pd

SHAP_ENABLED = os.getenv("ENABLE_SHAP", "0").lower() in {"1", "true", "yes"}

try:
    if not SHAP_ENABLED:
        raise ImportError("SHAP disabled by default")
    import shap  # type: ignore
except Exception:  # pragma: no cover
    shap = None


@dataclass(slots=True)
class Explainer:
    def explain_row(self, row: pd.Series) -> str:
        contributions = {
            "momentum": 0.35 * float(row.get("ret_5d", 0)) + 0.25 * float(row.get("ret_20d", 0)),
            "intraday": 0.15 * float(row.get("intraday_ret_1h", 0) or 0),
            "volatility_drag": -0.20 * float(row.get("rv_5d", 0) or 0),
            "gap_risk": -0.05 * abs(float(row.get("gap_pct", 0) or 0)),
        }
        ordered = sorted(contributions.items(), key=lambda kv: abs(kv[1]), reverse=True)
        return ", ".join(f"{name}={value:+.3f}" for name, value in ordered[:3])

    def summarize_model(self, model: object | None, features: pd.DataFrame, feature_cols: list[str]) -> dict:
        sample = features[feature_cols].fillna(0.0).tail(50)
        if shap is not None and model is not None and not sample.empty:
            try:
                explainer = shap.Explainer(model.predict, sample)
                values = explainer(sample)
                importance = pd.Series(abs(values.values).mean(axis=0), index=feature_cols).sort_values(ascending=False)
                return {"method": "shap", "top_features": importance.head(5).to_dict()}
            except Exception:
                pass
        if sample.empty:
            return {"method": "none", "top_features": {}}
        corr = sample.corrwith(sample.sum(axis=1)).abs().sort_values(ascending=False)
        return {"method": "correlation_proxy", "top_features": corr.head(5).to_dict()}
