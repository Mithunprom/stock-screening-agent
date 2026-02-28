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
    gross_long_short_return: float
    net_long_short_return: float
    avg_cost_bps: float
    hit_rate: float
    observations: int


def walk_forward_splits(dates: list[pd.Timestamp], min_train: int = 40, step: int = 5) -> list[tuple[list[pd.Timestamp], list[pd.Timestamp]]]:
    splits = []
    for i in range(min_train, len(dates), step):
        test_dates = dates[i : i + step]
        if not test_dates:
            continue
        splits.append((dates[:i], test_dates))
    return splits


def evaluate_rank_predictions(
    frame: pd.DataFrame,
    prediction_col: str,
    target_col: str,
    transaction_cost_bps: float = 10.0,
    slippage_bps: float = 5.0,
    top_n: int = 3,
) -> ValidationResult:
    by_day = []
    turnover = []
    prev_weights: dict[str, float] = {}
    total_costs = []
    for _, chunk in frame.groupby("date"):
        if chunk[prediction_col].notna().sum() < 3:
            continue
        ranked = chunk[[prediction_col, target_col, "ticker"]].dropna()
        if ranked.empty:
            continue
        ic = ranked[prediction_col].corr(ranked[target_col], method="spearman")
        top = ranked.nlargest(min(top_n, len(ranked)), prediction_col)
        bottom = ranked.nsmallest(min(top_n, len(ranked)), prediction_col)
        gross = top[target_col].mean() - bottom[target_col].mean()
        current_weights = {ticker: 1 / max(len(top), 1) for ticker in top["ticker"]}
        current_weights.update({ticker: -1 / max(len(bottom), 1) for ticker in bottom["ticker"]})
        all_tickers = set(current_weights) | set(prev_weights)
        current_turnover = 0.5 * sum(abs(current_weights.get(t, 0.0) - prev_weights.get(t, 0.0)) for t in all_tickers)
        prev_weights = current_weights
        turnover.append(current_turnover)
        cost = current_turnover * ((transaction_cost_bps + slippage_bps) / 10000)
        total_costs.append(cost)
        by_day.append((ic if pd.notna(ic) else 0.0, gross, gross - cost))
    ics = np.array([x[0] for x in by_day]) if by_day else np.array([0.0])
    gross_ls = np.array([x[1] for x in by_day]) if by_day else np.array([0.0])
    net_ls = np.array([x[2] for x in by_day]) if by_day else np.array([0.0])
    return ValidationResult(
        ic=float(ics.mean()),
        ic_ir=float(ics.mean() / (ics.std(ddof=0) + 1e-9)),
        turnover=float(np.mean(turnover) if turnover else 0.0),
        long_short_return=float(net_ls.mean()),
        gross_long_short_return=float(gross_ls.mean()),
        net_long_short_return=float(net_ls.mean()),
        avg_cost_bps=float((np.mean(total_costs) * 10000) if total_costs else 0.0),
        hit_rate=float(np.mean(net_ls > 0) if len(net_ls) else 0.0),
        observations=int(len(by_day)),
    )
