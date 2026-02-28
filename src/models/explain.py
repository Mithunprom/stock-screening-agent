from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


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

