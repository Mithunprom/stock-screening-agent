from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

try:
    from arch import arch_model  # type: ignore
except Exception:  # pragma: no cover
    arch_model = None


@dataclass(slots=True)
class VolModel:
    def fit_predict(self, features: pd.DataFrame) -> pd.DataFrame:
        rows = []
        for ticker, chunk in features.sort_values("date").groupby("ticker"):
            returns = chunk["ret_1d"].dropna()
            if len(returns) < 20:
                continue
            forecast = self._forecast_vol(returns)
            latest = chunk.iloc[-1]
            risk_score = min(1.0, forecast / max(float(latest.get("rv_20d", 0.2) or 0.2), 1e-3))
            rows.append(
                {
                    "date": latest["date"],
                    "ticker": ticker,
                    "forecast_vol": forecast,
                    "vol_risk_score": risk_score,
                }
            )
        return pd.DataFrame(rows)

    @staticmethod
    def _forecast_vol(returns: pd.Series) -> float:
        returns = returns.dropna()
        if arch_model is not None:
            try:
                model = arch_model(returns * 100, vol="Garch", p=1, q=1, dist="normal")
                result = model.fit(disp="off")
                forecast = result.forecast(horizon=1).variance.iloc[-1, 0]
                return float(np.sqrt(max(forecast, 0)) / 100 * np.sqrt(252))
            except Exception:  # pragma: no cover
                pass
        lam = 0.94
        variance = 0.0
        for ret in returns.tail(60):
            variance = lam * variance + (1 - lam) * ret**2
        return float(np.sqrt(variance) * np.sqrt(252))

