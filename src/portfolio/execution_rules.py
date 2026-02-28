from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.config import AppConfig


@dataclass(slots=True)
class ExecutionRules:
    settings: AppConfig

    def suggested_action(self, row: pd.Series, kill_switch_active: bool) -> str:
        if row.get("held_position", False):
            if row.get("close", 0) <= row.get("invalidation_price", float("-inf")):
                return "CONSIDER EXIT"
            if row.get("fused_confidence", 0) < 0.45 or row.get("risk_blocked", False):
                return "CONSIDER EXIT"
            return "HOLD"
        if row.get("risk_blocked", False):
            return "WATCH"
        if kill_switch_active:
            return "HOLD"
        if row.get("fused_confidence", 0) >= 0.60 and row.get("risk_grade") in {"A", "B"}:
            return "CONSIDER ENTRY"
        if row.get("fused_confidence", 0) >= 0.52:
            return "WATCH"
        return "HOLD"
