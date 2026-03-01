from __future__ import annotations

from datetime import datetime, timedelta
from math import cos, sin


def sample_dashboard() -> dict:
    now = datetime.now()
    recommendations = []
    base_rows = [
        ("LMT", "Industrials", "CONSIDER ENTRY", 487.22, 0.78, "High", "3-10 days", 0.74, "OK", 0.34, 0.028, 1_280_000_000, "geopolitical shock", 0.86, 0.72, 1.24, 0.67, 0.41, 472.4, "Defense flows strengthened after fresh geopolitical headlines, realized volatility remains tradeable, and cross-sectional momentum is leading the sector.", "A confidence drop below 0.58, a reversal through the invalidation level, or de-escalation in the catalyst tape.", "Headline-driven; expect gap risk if the geopolitical narrative fades.", "Defense tape + positive factor spread + contained risk."),
        ("NVDA", "Technology", "WATCH", 912.33, 0.73, "Strong", "1-5 days", 0.69, "OK", 0.49, 0.037, 5_200_000_000, "analyst action", 0.71, 0.58, 1.08, 0.51, 0.54, 880.1, "Semis remain the leadership group, news tone is constructive, and the ensemble still favors upside despite elevated realized volatility.", "Loss of semiconductor leadership, risk score above 0.70, or a close below 880.1.", "High-beta name; gaps can outrun stops.", "Leadership sector + supportive analyst tape."),
        ("XLE", "Energy", "WATCH", 95.28, 0.67, "Strong", "3-10 days", 0.63, "OK", 0.29, 0.022, 890_000_000, "macro shock", 0.59, 0.44, 0.92, 0.40, 0.35, 92.7, "Energy is showing better relative momentum, macro-sensitive names are firm, and the volatility regime is still manageable.", "Oil-sensitive headlines rolling over or XLE closing below 92.7.", "Macro-sensitive; correlation to broader risk assets can rise quickly.", "Sector rotation improving with calmer vol."),
        ("AAPL", "Technology", "HOLD", 188.41, 0.59, "Developing", "1-5 days", 0.57, "OK", 0.21, 0.018, 3_900_000_000, "company news", 0.44, 0.31, 0.66, 0.22, 0.28, 183.6, "Liquidity remains strong and signals lean positive, but upside edge is weaker than the top setups.", "New product catalyst or a breakout in factor leadership.", "Mega-cap drift can stall without catalyst support.", "Liquid and stable, but less asymmetric."),
        ("TSLA", "Consumer", "CONSIDER EXIT", 176.88, 0.31, "Low", "1-3 days", 0.34, "RISKY", 0.71, 0.062, 4_400_000_000, "company news", 0.51, 0.81, -0.42, -0.31, 0.82, 171.1, "Volatility is elevated, the time-series model rolled over, and the risk engine is now blocking fresh entries.", "Risk score cooling below 0.65 and confidence recovering above 0.50.", "Can whipsaw quickly around news.", "High vol + risk block + weak signal."),
    ]
    for idx in range(20):
        seed = idx % len(base_rows)
        row = list(base_rows[seed])
        row[0] = f"{row[0]}{idx}" if idx >= len(base_rows) else row[0]
        row[4] = max(0.14, row[4] - 0.02 * idx)
        row[7] = max(0.18, row[7] - 0.018 * idx)
        recommendations.append(
            {
                "ticker": row[0],
                "sector": row[1],
                "action": row[2] if idx < 5 else "WATCH",
                "close": row[3],
                "opportunity_score": row[4],
                "conviction_label": row[5] if idx < 5 else "Developing",
                "hold_horizon": row[6],
                "fused_confidence": row[7],
                "risk_label": row[8],
                "rv_5d": row[9],
                "atr_pct": row[10],
                "avg_dollar_volume_20d": row[11],
                "catalyst": row[12],
                "catalyst_confidence": row[13],
                "event_risk_score": row[14],
                "xsec_score": row[15],
                "ts_score": row[16],
                "vol_risk_score": row[17],
                "invalidation_price": row[18],
                "why": row[19],
                "what_changes": row[20],
                "caveats": row[21],
                "why_short": row[22],
            }
        )
    news = [
        {
            "id": "n1",
            "ticker": "LMT",
            "headline": "Defense names firm as new geopolitical risk premium enters the tape",
            "summary": "Defense complex outperformed after overnight headlines increased focus on procurement and security spending.",
            "impactScore": 84,
            "publishedAt": (now - timedelta(minutes=22)).isoformat(),
            "source": "Public RSS",
            "catalyst": "geopolitical shock",
        },
        {
            "id": "n2",
            "ticker": "NVDA",
            "headline": "Chip demand narrative remains constructive after fresh analyst upgrades",
            "summary": "Analyst tone improved with stronger data-center checks and higher long-term AI infrastructure assumptions.",
            "impactScore": 73,
            "publishedAt": (now - timedelta(minutes=55)).isoformat(),
            "source": "Public RSS",
            "catalyst": "analyst action",
        },
    ]
    return {
        "as_of": now.isoformat(),
        "market_context": {
            "spy_last": 584.2,
            "spy_ret_1d": -0.004,
            "spy_rv_5d": 0.19,
            "qqq_last": 513.7,
            "qqq_ret_1d": 0.006,
            "qqq_rv_5d": 0.22,
            "risk_regime": "Elevated but tradeable",
        },
        "recommendations": recommendations,
        "watchlist": recommendations[:5],
        "positions": [
            {
                "ticker": "LMT",
                "quantity": 1.8,
                "avg_entry": 481.4,
                "mark": 487.22,
                "market_value": 877.0,
                "unrealized_pnl": 10.48,
                "pnl_pct": 0.0121,
                "action": "CONSIDER ENTRY",
                "conviction_label": "High",
                "hold_horizon": "3-10 days",
                "risk_label": "OK",
                "invalidation_price": 472.4,
            }
        ],
        "portfolio_state": {
            "cash": 612.14,
            "day_start_equity": 1965.88,
            "current_day": now.strftime("%Y-%m-%d"),
            "kill_switch_active": False,
            "realized_pnl": 43.28,
            "equityCurve": [
                {
                    "timestamp": (now - timedelta(hours=(19 - i))).isoformat(),
                    "equity": 1700 + i * 12 + sin(i / 2) * 18,
                }
                for i in range(20)
            ],
        },
        "paper_actions": [{"ticker": "LMT", "paper_action": "ENTRY", "qty": 1.8, "price": 481.4}],
        "news": news,
        "model_freshness": {
            "factor": (now - timedelta(minutes=55)).isoformat(),
            "deep": (now - timedelta(minutes=80)).isoformat(),
            "baseline": (now - timedelta(minutes=70)).isoformat(),
            "volatility": (now - timedelta(minutes=40)).isoformat(),
        },
        "data_status": {
            "latencyMs": 850,
            "level": "green",
            "feed": "sample-mode",
            "note": "Using cached snapshot with deterministic sample candles.",
        },
        "backtest_summary": {
            "ic": 0.08,
            "ic_ir": 0.64,
            "hit_rate": 0.57,
            "disclaimer": "Validation metrics are indicative research diagnostics, not a guarantee of future outcomes.",
        },
    }


def sample_quote(ticker: str) -> dict:
    dashboard = sample_dashboard()
    row = next((item for item in dashboard["recommendations"] if item["ticker"] == ticker), None)
    base = float(row["close"]) if row else 100.0
    bump = ((ord(ticker[0]) % 9) - 4) / 100 if ticker else 0
    return {
        "ticker": ticker,
        "price": round(base * (1 + bump / 10), 2),
        "changePct": bump,
        "updatedAt": datetime.now().isoformat(),
        "source": "sample-mode",
    }


def sample_candles(ticker: str, range_name: str, interval: str) -> list[dict]:
    steps_by_range = {"1D": 60, "5D": 80, "1M": 50, "6M": 90, "1Y": 120}
    count = steps_by_range.get(range_name, 60)
    seed = sum(ord(ch) for ch in ticker) if ticker else 1
    base = sample_quote(ticker)["price"]
    candles = []
    prev_close = base * 0.94
    cumulative_volume = 0.0
    cumulative_pv = 0.0
    recent_closes: list[float] = []
    now = datetime.now()
    for index in range(count):
        wave = sin((index + seed) / 7) * 1.8
        drift = ((seed % 5) - 2) * 0.08
        open_px = prev_close
        close = max(2.0, open_px + wave + drift)
        high = max(open_px, close) + 1.2 + abs(sin(index)) * 0.6
        low = min(open_px, close) - 1.1 - abs(cos(index)) * 0.4
        volume = 400000 + ((seed * (index + 3)) % 1600000)
        cumulative_volume += volume
        cumulative_pv += close * volume
        recent_closes.append(close)
        ma20_window = recent_closes[-20:]
        ma50_window = recent_closes[-50:]
        ma20 = sum(ma20_window) / len(ma20_window)
        ma50 = sum(ma50_window) / len(ma50_window)
        atr = (high - low) * 0.85
        candles.append(
            {
                "time": (now - timedelta(milliseconds=(count - index) * interval_to_ms(interval))).isoformat(),
                "open": round(open_px, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "close": round(close, 2),
                "volume": volume,
                "vwap": round(cumulative_pv / cumulative_volume, 2),
                "ma20": round(ma20, 2),
                "ma50": round(ma50, 2),
                "atrHigh": round(close + atr, 2),
                "atrLow": round(close - atr, 2),
            }
        )
        prev_close = close
    return candles


def sample_preferences() -> dict:
    return {
        "onboardingComplete": False,
        "riskTolerance": "Balanced",
        "alertChannel": "email",
        "watchlist": [
            {
                "ticker": "LMT",
                "enabled": True,
                "confidenceDeltaThreshold": 0.07,
                "predictedMoveThreshold": 0.04,
                "riskDowngradeAlert": True,
                "majorNewsAlert": True,
                "cooldownMinutes": 90,
            }
        ],
    }


def interval_to_ms(interval: str) -> int:
    mapping = {
        "1m": 60_000,
        "5m": 5 * 60_000,
        "15m": 15 * 60_000,
        "1h": 60 * 60_000,
        "1d": 24 * 60 * 60_000,
    }
    return mapping.get(interval, 60 * 60_000)
