from __future__ import annotations

SECTOR_MAP = {
    "AAPL": "Technology",
    "MSFT": "Technology",
    "NVDA": "Technology",
    "AMZN": "Consumer",
    "META": "Communication",
    "TSLA": "Consumer",
    "AMD": "Technology",
    "SMCI": "Technology",
    "PLTR": "Technology",
    "NFLX": "Communication",
    "AVGO": "Technology",
    "JPM": "Financials",
    "BAC": "Financials",
    "XOM": "Energy",
    "CVX": "Energy",
    "LLY": "Healthcare",
    "UNH": "Healthcare",
    "COIN": "Financials",
    "SHOP": "Technology",
    "UBER": "Industrials",
    "SPY": "Index",
    "QQQ": "Index",
    "IWM": "Index",
    "XLF": "Financials",
    "XLK": "Technology",
    "XLE": "Energy",
    "XLY": "Consumer",
    "XLV": "Healthcare",
}


def get_sector(ticker: str) -> str:
    return SECTOR_MAP.get(ticker, "Other")
