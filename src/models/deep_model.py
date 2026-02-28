from __future__ import annotations

from dataclasses import dataclass
import os

import numpy as np
import pandas as pd

from src.models.validation import walk_forward_splits

TORCH_ENABLED = os.getenv("ENABLE_TORCH", "0").lower() in {"1", "true", "yes"}

try:
    if not TORCH_ENABLED:
        raise ImportError("PyTorch disabled by default for stable local dry-runs")
    import torch
    import torch.nn as nn
except Exception:  # pragma: no cover
    torch = None
    nn = None


@dataclass(slots=True)
class DeepForecastResult:
    signal: pd.DataFrame
    metadata: dict


if nn is not None:  # pragma: no cover
    class _LSTMRegressor(nn.Module):
        def __init__(self, input_size: int, hidden_size: int = 16, dropout: float = 0.2) -> None:
            super().__init__()
            self.lstm = nn.LSTM(input_size=input_size, hidden_size=hidden_size, batch_first=True)
            self.dropout = nn.Dropout(dropout)
            self.out = nn.Linear(hidden_size, 1)

        def forward(self, x):
            output, _ = self.lstm(x)
            hidden = self.dropout(output[:, -1, :])
            return self.out(hidden)
else:
    _LSTMRegressor = None


@dataclass(slots=True)
class DeepTimeSeriesModel:
    sequence_length: int = 20
    epochs: int = 10
    mc_samples: int = 10

    def fit_predict(self, features: pd.DataFrame, horizon_label: str = "ret_1d") -> DeepForecastResult:
        if torch is None or nn is None:
            signal = self._fallback_predict(features, horizon_label)
            return DeepForecastResult(signal=signal, metadata=self._validation_metadata(signal, features, "heuristic"))
        signal = self._torch_predict(features, horizon_label)
        return DeepForecastResult(signal=signal, metadata=self._validation_metadata(signal, features, "torch"))

    def _fallback_predict(self, features: pd.DataFrame, horizon_label: str) -> pd.DataFrame:
        df = features.sort_values(["ticker", "date"]).copy()
        rows = []
        for _, test_dates in walk_forward_splits(sorted(df["date"].dropna().unique().tolist()), min_train=40, step=5):
            chunk = df[df["date"].isin(test_dates)].copy()
            chunk["ts_score"] = (
                0.45 * chunk["ret_5d"].fillna(0)
                + 0.25 * chunk["ret_20d"].fillna(0)
                + 0.15 * chunk["sector_relative_momentum_5d"].fillna(0)
                - 0.20 * chunk["rv_5d"].fillna(df["rv_5d"].median())
                + 0.15 * chunk["intraday_ret_1h"].fillna(0)
            )
            rows.append(chunk[["date", "ticker", "ts_score"]])
        pred = pd.concat(rows, ignore_index=True) if rows else df[["date", "ticker"]].copy()
        df = df.merge(pred, on=["date", "ticker"], how="left")
        fill = (
            0.45 * df["ret_5d"].fillna(0)
            + 0.25 * df["ret_20d"].fillna(0)
            + 0.15 * df["sector_relative_momentum_5d"].fillna(0)
            - 0.20 * df["rv_5d"].fillna(df["rv_5d"].median())
            + 0.15 * df["intraday_ret_1h"].fillna(0)
        )
        df["ts_score"] = df["ts_score"].fillna(fill)
        uncertainty = df.groupby("ticker")["ret_1d"].transform(lambda x: x.rolling(20).std(ddof=0)).fillna(df["rv_5d"])
        df["ts_uncertainty"] = uncertainty.fillna(uncertainty.median()).clip(lower=0.001)
        return df[["date", "ticker", "ts_score", "ts_uncertainty"]]

    def _torch_predict(self, features: pd.DataFrame, horizon_label: str) -> pd.DataFrame:  # pragma: no cover
        df = features.sort_values(["ticker", "date"]).copy()
        feature_cols = ["ret_1d", "ret_5d", "ret_20d", "rv_5d", "gap_pct", "range_pct", "intraday_ret_1h"]
        rows = []
        for ticker, chunk in df.groupby("ticker"):
            chunk = chunk.dropna(subset=feature_cols + [horizon_label]).copy()
            if len(chunk) <= self.sequence_length + 5:
                continue
            values = chunk[feature_cols].fillna(0.0).to_numpy(dtype=np.float32)
            targets = chunk[horizon_label].to_numpy(dtype=np.float32)
            X, y, dates = [], [], []
            for i in range(self.sequence_length, len(chunk)):
                X.append(values[i - self.sequence_length : i])
                y.append(targets[i])
                dates.append(chunk.iloc[i]["date"])
            X_t = torch.tensor(np.array(X))
            y_t = torch.tensor(np.array(y)).reshape(-1, 1)
            model = _LSTMRegressor(input_size=len(feature_cols))
            optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
            loss_fn = nn.MSELoss()
            model.train()
            for _ in range(self.epochs):
                optimizer.zero_grad()
                pred = model(X_t)
                loss = loss_fn(pred, y_t)
                loss.backward()
                optimizer.step()
            model.train()
            preds = []
            for _ in range(self.mc_samples):
                preds.append(model(X_t).detach().numpy().reshape(-1))
            pred_arr = np.vstack(preds)
            means = pred_arr.mean(axis=0)
            stds = pred_arr.std(axis=0) + 1e-4
            for dt, mean, std in zip(dates, means, stds):
                rows.append({"date": dt, "ticker": ticker, "ts_score": float(mean), "ts_uncertainty": float(std)})
        if not rows:
            return self._fallback_predict(features, horizon_label)
        return pd.DataFrame(rows)

    @staticmethod
    def _validation_metadata(signal: pd.DataFrame, features: pd.DataFrame, backend: str) -> dict:
        merged = signal.merge(
            features.sort_values(["ticker", "date"]).assign(target_next_1d=lambda x: x.groupby("ticker")["ret_1d"].shift(-1))[["date", "ticker", "target_next_1d"]],
            on=["date", "ticker"],
            how="left",
        ).dropna(subset=["ts_score", "target_next_1d"])
        if merged.empty:
            return {"backend": backend, "directional_accuracy": 0.0, "mae": None}
        directional = float(np.mean(np.sign(merged["ts_score"]) == np.sign(merged["target_next_1d"])))
        mae = float(np.mean(np.abs(merged["ts_score"] - merged["target_next_1d"])))
        return {"backend": backend, "directional_accuracy": directional, "mae": mae}
