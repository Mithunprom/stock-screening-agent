from __future__ import annotations

import asyncio
import json

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from src.api_service.service import ResearchApiService

app = FastAPI(title="Stock Screening Agent API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
service = ResearchApiService()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/dashboard")
def dashboard() -> dict:
    return service.dashboard()


@app.get("/api/market/quote")
def market_quote(ticker: str = Query(...)) -> dict:
    return service.quote(ticker.upper())


@app.get("/api/market/candles")
def market_candles(ticker: str = Query(...), interval: str = "1h", range: str = "1M") -> dict:
    return service.candles(ticker.upper(), range, interval)


@app.get("/api/screener/top-volatile")
def top_volatile(window: str = "5d", limit: int = 20) -> dict:
    payload = service.top_volatile(limit)
    payload["window"] = window
    return payload


@app.get("/api/news/latest")
def latest_news(tickers: str = "", since: str | None = None) -> dict:
    del since
    parsed = [item.strip().upper() for item in tickers.split(",") if item.strip()]
    return {"rows": service.latest_news(parsed)}


@app.get("/api/signals/summary")
def signals_summary(ticker: str = Query(...)) -> dict:
    return service.signal_summary(ticker.upper())


@app.get("/api/portfolio/state")
def portfolio_state() -> dict:
    return service.portfolio_state()


@app.get("/api/preferences")
def preferences() -> dict:
    return service.preferences()


@app.post("/api/preferences")
async def save_preferences(payload: dict) -> dict:
    return service.save_preferences(payload)


@app.get("/api/watchlist")
def watchlist() -> list[dict]:
    return service.preferences().get("watchlist", [])


@app.post("/api/watchlist")
async def update_watchlist(payload: dict) -> list[dict]:
    if "ticker" not in payload:
        raise HTTPException(status_code=400, detail="ticker is required")
    return service.update_watchlist(payload)


@app.get("/api/stream/updates")
async def stream_updates(tickers: str = "") -> StreamingResponse:
    parsed = [item.strip().upper() for item in tickers.split(",") if item.strip()][:8]

    async def event_generator():
        while True:
            quotes = [service.quote(ticker) for ticker in parsed]
            yield f"data: {json.dumps({'quotes': quotes})}\n\n"
            await asyncio.sleep(10)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
