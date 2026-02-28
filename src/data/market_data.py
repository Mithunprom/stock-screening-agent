from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from src.config import AppConfig
from src.utils.logging import get_logger

logger = get_logger(__name__)

YFINANCE_ENABLED = os.getenv("ENABLE_YFINANCE", "0").lower() in {"1", "true", "yes"}

try:
    if not YFINANCE_ENABLED:
        raise ImportError("yfinance disabled by default for stable offline execution")
    import yfinance as yf  # type: ignore
except Exception:  # pragma: no cover
    yf = None


SAMPLE_BASE = {
    "AAPL": 188.0,
    "MSFT": 421.0,
    "NVDA": 902.0,
    "AMZN": 176.0,
    "META": 497.0,
    "TSLA": 198.0,
    "AMD": 172.0,
    "SMCI": 880.0,
    "PLTR": 28.0,
    "NFLX": 612.0,
    "AVGO": 1287.0,
    "JPM": 199.0,
    "BAC": 37.0,
    "XOM": 108.0,
    "CVX": 151.0,
    "LLY": 781.0,
    "UNH": 502.0,
    "COIN": 219.0,
    "SHOP": 84.0,
    "UBER": 76.0,
    "SPY": 588.0,
    "QQQ": 517.0,
    "IWM": 212.0,
    "XLF": 48.0,
    "XLK": 237.0,
    "XLE": 88.0,
    "XLY": 191.0,
    "XLV": 147.0,
}


@dataclass(slots=True)
class MarketDataAdapter:
    settings: AppConfig

    @property
    def cache_path(self) -> Path:
        return self.settings.cache_dir / "market_daily.parquet"

    def fetch_daily_history(self, tickers: Iterable[str], lookback_days: int | None = None) -> pd.DataFrame:
        lookback_days = lookback_days or self.settings.lookback_days
        tickers = list(dict.fromkeys(tickers))
        start = datetime.now(timezone.utc).date() - timedelta(days=max(lookback_days * 2, 120))
        if yf is not None:
            try:
                frame = yf.download(
                    tickers=tickers,
                    start=str(start),
                    progress=False,
                    group_by="ticker",
                    auto_adjust=False,
                    threads=True,
                )
                data = self._normalize_download(frame, tickers)
                if not data.empty:
                    self._cache_frame(data, self.cache_path)
                    return data
            except Exception as exc:  # pragma: no cover
                logger.warning("yfinance daily fetch failed: %s", exc)
        if self.cache_path.exists():
            try:
                return pd.read_parquet(self.cache_path)
            except Exception:
                logger.warning("Failed to read cached daily market data")
        return self._build_sample_daily(tickers, lookback_days)

    def fetch_intraday_history(self, tickers: Iterable[str], period: str = "5d", interval: str = "60m") -> pd.DataFrame:
        tickers = list(dict.fromkeys(tickers))
        cache_path = self.settings.cache_dir / f"market_intraday_{interval}.parquet"
        if yf is not None:
            try:
                frame = yf.download(
                    tickers=tickers,
                    period=period,
                    interval=interval,
                    progress=False,
                    group_by="ticker",
                    auto_adjust=False,
                    threads=True,
                )
                data = self._normalize_download(frame, tickers)
                if not data.empty:
                    self._cache_frame(data, cache_path)
                    return data
            except Exception as exc:  # pragma: no cover
                logger.warning("yfinance intraday fetch failed: %s", exc)
        if cache_path.exists():
            try:
                return pd.read_parquet(cache_path)
            except Exception:
                logger.warning("Failed to read cached intraday market data")
        return self._build_sample_intraday(tickers)

    def latest_snapshot(self, tickers: Iterable[str]) -> pd.DataFrame:
        daily = self.fetch_daily_history(tickers)
        latest = (
            daily.sort_values("date")
            .groupby("ticker")
            .tail(1)
            .set_index("ticker")[["open", "high", "low", "close", "volume"]]
            .reset_index()
        )
        latest["dollar_volume"] = latest["close"] * latest["volume"]
        return latest

    @staticmethod
    def _cache_frame(data: pd.DataFrame, path: Path) -> None:
        try:
            data.to_parquet(path, index=False)
        except Exception:
            data.to_csv(path.with_suffix(".csv"), index=False)

    @staticmethod
    def _normalize_download(frame: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
        if frame.empty:
            return pd.DataFrame(columns=["date", "ticker", "open", "high", "low", "close", "adj_close", "volume"])
        if isinstance(frame.columns, pd.MultiIndex):
            chunks: list[pd.DataFrame] = []
            for ticker in tickers:
                if ticker not in frame.columns.get_level_values(0):
                    continue
                sub = frame[ticker].copy()
                sub.columns = [c.lower().replace(" ", "_") for c in sub.columns]
                sub["date"] = pd.to_datetime(sub.index, utc=True).tz_localize(None)
                sub["ticker"] = ticker
                chunks.append(sub.reset_index(drop=True))
            return pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()
        data = frame.copy()
        data.columns = [c.lower().replace(" ", "_") for c in data.columns]
        data["date"] = pd.to_datetime(data.index, utc=True).tz_localize(None)
        data["ticker"] = tickers[0] if tickers else "UNKNOWN"
        return data.reset_index(drop=True)

    @staticmethod
    def _build_sample_daily(tickers: list[str], lookback_days: int) -> pd.DataFrame:
        rng = np.random.default_rng(7)
        dates = pd.bdate_range(end=pd.Timestamp.utcnow().normalize(), periods=lookback_days)
        rows = []
        for idx, ticker in enumerate(tickers):
            base = SAMPLE_BASE.get(ticker, 20.0 + idx * 3)
            level = base
            vol_scale = 0.012 + (idx % 7) * 0.005
            for dt in dates:
                ret = rng.normal(0.0008, vol_scale)
                gap = rng.normal(0.0, vol_scale / 2)
                open_px = max(1.0, level * (1 + gap))
                close = max(1.0, open_px * (1 + ret))
                high = max(open_px, close) * (1 + abs(rng.normal(0, vol_scale / 2)))
                low = min(open_px, close) * (1 - abs(rng.normal(0, vol_scale / 2)))
                volume = int(abs(rng.normal(5_000_000 + idx * 250_000, 1_000_000)))
                rows.append(
                    {
                        "date": pd.Timestamp(dt).to_pydatetime(),
                        "ticker": ticker,
                        "open": round(open_px, 2),
                        "high": round(high, 2),
                        "low": round(low, 2),
                        "close": round(close, 2),
                        "adj_close": round(close, 2),
                        "volume": volume,
                    }
                )
                level = close
        return pd.DataFrame(rows)

    @staticmethod
    def _build_sample_intraday(tickers: list[str]) -> pd.DataFrame:
        rng = np.random.default_rng(11)
        dates = pd.date_range(end=pd.Timestamp.utcnow().floor("h"), periods=35, freq="h")
        rows = []
        for idx, ticker in enumerate(tickers):
            level = SAMPLE_BASE.get(ticker, 20.0 + idx * 3)
            vol_scale = 0.004 + (idx % 5) * 0.002
            for dt in dates:
                ret = rng.normal(0.0, vol_scale)
                open_px = level
                close = max(1.0, open_px * (1 + ret))
                high = max(open_px, close) * (1 + abs(rng.normal(0, vol_scale / 2)))
                low = min(open_px, close) * (1 - abs(rng.normal(0, vol_scale / 2)))
                volume = int(abs(rng.normal(600_000 + idx * 40_000, 150_000)))
                rows.append(
                    {
                        "date": pd.Timestamp(dt).to_pydatetime(),
                        "ticker": ticker,
                        "open": round(open_px, 2),
                        "high": round(high, 2),
                        "low": round(low, 2),
                        "close": round(close, 2),
                        "adj_close": round(close, 2),
                        "volume": volume,
                    }
                )
                level = close
        return pd.DataFrame(rows)
