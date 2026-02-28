from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(slots=True)
class ValidationResult:
    ic: float
    ic_ir: float
    turnover: float
    long_short_return: float
    observations: int


def walk_forward_splits(dates: list[pd.Timestamp], min_train: int = 40, step: int = 5) -> list[tuple[list[pd.Timestamp], list[pd.Timestamp]]]:
    splits = []
    for i in range(min_train, len(dates) - step, step):
        splits.append((dates[:i], dates[i : i + step]))
    return splits


def evaluate_rank_predictions(frame: pd.DataFrame, prediction_col: str, target_col: str) -> ValidationResult:
    by_day = []
    turnover = []
    prev_top: set[str] = set()
    for day, chunk in frame.groupby("date"):
        if chunk[prediction_col].notna().sum() < 3:
            continue
        ranked = chunk[[prediction_col, target_col, "ticker"]].dropna()
        if ranked.empty:
            continue
        ic = ranked[prediction_col].corr(ranked[target_col], method="spearman")
        top = set(ranked.nlargest(min(5, len(ranked)), prediction_col)["ticker"])
        if prev_top:
            turnover.append(1 - len(top & prev_top) / max(len(top), 1))
        prev_top = top
        long_short = ranked.nlargest(3, prediction_col)[target_col].mean() - ranked.nsmallest(3, prediction_col)[target_col].mean()
        by_day.append((ic if pd.notna(ic) else 0.0, long_short))
    ics = np.array([x[0] for x in by_day]) if by_day else np.array([0.0])
    ls = np.array([x[1] for x in by_day]) if by_day else np.array([0.0])
    return ValidationResult(
        ic=float(ics.mean()),
        ic_ir=float(ics.mean() / (ics.std(ddof=0) + 1e-9)),
        turnover=float(np.mean(turnover) if turnover else 0.0),
        long_short_return=float(ls.mean()),
        observations=int(len(by_day)),
    )

