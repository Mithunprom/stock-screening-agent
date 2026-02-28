from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import os
from typing import Iterable
from xml.etree import ElementTree

import pandas as pd
import requests

from src.config import AppConfig
from src.utils.logging import get_logger

logger = get_logger(__name__)

FINANCE_FEEDS = [
    "https://feeds.finance.yahoo.com/rss/2.0/headline",
    "https://www.sec.gov/rss/litigation/litreleases.xml",
]

POSITIVE_WORDS = {"beat", "upgrade", "record", "growth", "surge", "profit", "wins", "guidance", "contract", "award", "order"}
NEGATIVE_WORDS = {"miss", "downgrade", "probe", "lawsuit", "fraud", "cut", "loss", "plunge", "ceasefire"}
FINBERT_ENABLED = os.getenv("ENABLE_FINBERT", "0").lower() in {"1", "true", "yes"}

try:
    if not FINBERT_ENABLED:
        raise ImportError("FinBERT disabled by default")
    from transformers import pipeline  # type: ignore
except Exception:  # pragma: no cover
    pipeline = None


@dataclass(slots=True)
class NewsDataAdapter:
    settings: AppConfig
    _sentiment_model: object | None = field(init=False, default=None, repr=False)

    def __post_init__(self) -> None:
        self._sentiment_model = None
        if pipeline is not None:
            try:
                self._sentiment_model = pipeline("text-classification", model="ProsusAI/finbert", tokenizer="ProsusAI/finbert")
            except Exception:
                self._sentiment_model = None

    def fetch_news(self, tickers: Iterable[str], lookback_hours: int = 48) -> pd.DataFrame:
        tickers = list(dict.fromkeys(tickers))
        cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
        rows: list[dict] = []
        for url in FINANCE_FEEDS:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                rows.extend(self._parse_feed(response.text, tickers, cutoff))
            except Exception as exc:  # pragma: no cover
                logger.warning("News fetch failed from %s: %s", url, exc)
        if not rows:
            return self._sample_news(tickers)
        frame = pd.DataFrame(rows)
        frame["cluster_key"] = frame["headline"].map(self._cluster_key)
        frame = frame.sort_values(["ticker", "published"], ascending=[True, False]).drop_duplicates(subset=["ticker", "cluster_key"])
        return frame.sort_values(["ticker", "published"], ascending=[True, False]).reset_index(drop=True)

    def summarize(self, news: pd.DataFrame) -> pd.DataFrame:
        if news.empty:
            return pd.DataFrame(columns=["ticker", "headline_count", "sentiment", "catalyst", "narrative"])
        grouped = news.groupby("ticker")
        rows = []
        for ticker, chunk in grouped:
            sentiment = float(chunk["sentiment"].mean())
            catalyst = chunk["catalyst"].mode().iloc[0] if not chunk["catalyst"].mode().empty else "none"
            top = chunk.head(2)["headline"].tolist()
            event_risk_score = float(min(1.0, abs(sentiment) * 0.5 + len(chunk) / 10))
            catalyst_confidence = float(min(1.0, len(chunk) / 4))
            rows.append(
                {
                    "ticker": ticker,
                    "headline_count": int(len(chunk)),
                    "sentiment": sentiment,
                    "catalyst": catalyst,
                    "event_risk_score": event_risk_score,
                    "catalyst_confidence": catalyst_confidence,
                    "narrative": "; ".join(top),
                }
            )
        return pd.DataFrame(rows)

    def _parse_feed(self, xml_text: str, tickers: list[str], cutoff: datetime) -> list[dict]:
        rows: list[dict] = []
        root = ElementTree.fromstring(xml_text)
        items = root.findall(".//item")
        for item in items:
            title = (item.findtext("title") or "").strip()
            description = (item.findtext("description") or "").strip()
            pub_date = item.findtext("pubDate") or ""
            published = self._parse_pub_date(pub_date)
            if published is not None and published < cutoff:
                continue
            text = f"{title} {description}".upper()
            matched = [ticker for ticker in tickers if ticker.upper() in text]
            for ticker in matched:
                sentiment = self._score_sentiment(f"{title} {description}")
                catalyst = self._detect_catalyst(f"{title} {description}")
                rows.append(
                    {
                        "ticker": ticker,
                        "headline": title,
                        "snippet": description,
                        "published": (published or datetime.now(timezone.utc)).isoformat(),
                        "sentiment": sentiment,
                        "catalyst": catalyst,
                    }
                )
        return rows

    @staticmethod
    def _parse_pub_date(text: str) -> datetime | None:
        if not text:
            return None
        from email.utils import parsedate_to_datetime

        try:
            return parsedate_to_datetime(text).astimezone(timezone.utc)
        except Exception:
            return None

    @staticmethod
    def _heuristic_score_sentiment(text: str) -> float:
        lowered = text.lower()
        score = sum(word in lowered for word in POSITIVE_WORDS) - sum(word in lowered for word in NEGATIVE_WORDS)
        return max(-1.0, min(1.0, score / 3))

    def _score_sentiment(self, text: str) -> float:  # type: ignore[override]
        if self._sentiment_model is not None:
            try:
                result = self._sentiment_model(text[:512])[0]
                label = result["label"].lower()
                score = float(result["score"])
                if "negative" in label:
                    return -score
                if "positive" in label:
                    return score
                return 0.0
            except Exception:
                pass
        return self._heuristic_score_sentiment(text)

    @staticmethod
    def _detect_catalyst(text: str) -> str:
        lowered = text.lower()
        if any(term in lowered for term in {"war", "conflict", "missile", "strike", "pentagon", "nato", "defense", "military", "invasion"}):
            return "geopolitical shock"
        if "earnings" in lowered:
            return "earnings"
        if "guidance" in lowered:
            return "guidance"
        if "analyst" in lowered or "upgrade" in lowered or "downgrade" in lowered:
            return "analyst action"
        if "10-k" in lowered or "8-k" in lowered or "sec" in lowered:
            return "sec filing"
        if "inflation" in lowered or "rates" in lowered or "fed" in lowered:
            return "macro shock"
        return "company news"

    @staticmethod
    def _sample_news(tickers: list[str]) -> pd.DataFrame:
        rows = []
        for i, ticker in enumerate(tickers[:12]):
            rows.append(
                {
                    "ticker": ticker,
                    "headline": f"{ticker} sees notable volume and momentum into the session",
                    "snippet": f"{ticker} remains active with elevated volatility and broad market attention.",
                    "published": datetime.now(timezone.utc).isoformat(),
                    "sentiment": 0.2 if i % 3 else -0.1,
                    "catalyst": "company news" if i % 4 else "analyst action",
                }
            )
        return pd.DataFrame(rows)

    @staticmethod
    def _cluster_key(text: str) -> str:
        lowered = "".join(ch.lower() if ch.isalnum() or ch.isspace() else " " for ch in text)
        parts = [part for part in lowered.split() if len(part) > 2]
        return " ".join(parts[:8])
