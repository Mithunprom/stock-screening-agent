from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.config import AppConfig
from src.utils.io import read_json, write_json


@dataclass(slots=True)
class Position:
    ticker: str
    quantity: float
    avg_entry: float


@dataclass(slots=True)
class PortfolioState:
    cash: float
    positions: dict[str, Position] = field(default_factory=dict)
    day_start_equity: float = 0.0
    current_day: str = ""
    kill_switch_active: bool = False
    realized_pnl: float = 0.0


class PaperPortfolio:
    def __init__(self, settings: AppConfig) -> None:
        self.settings = settings
        self.path = settings.state_dir / "paper_portfolio.json"
        self.state = self._load()

    def _load(self) -> PortfolioState:
        raw = read_json(self.path, {})
        if not raw:
            return PortfolioState(cash=self.settings.starting_cash)
        positions = {
            ticker: Position(**pos)
            for ticker, pos in raw.get("positions", {}).items()
        }
        return PortfolioState(
            cash=raw.get("cash", self.settings.starting_cash),
            positions=positions,
            day_start_equity=raw.get("day_start_equity", self.settings.starting_cash),
            current_day=raw.get("current_day", ""),
            kill_switch_active=raw.get("kill_switch_active", False),
            realized_pnl=raw.get("realized_pnl", 0.0),
        )

    def save(self) -> None:
        payload = asdict(self.state)
        payload["positions"] = {k: asdict(v) for k, v in self.state.positions.items()}
        write_json(self.path, payload)

    def positions_frame(self, prices: dict[str, float] | None = None) -> pd.DataFrame:
        prices = prices or {}
        rows = []
        for ticker, pos in self.state.positions.items():
            mark = prices.get(ticker, pos.avg_entry)
            rows.append(
                {
                    "ticker": ticker,
                    "quantity": pos.quantity,
                    "avg_entry": pos.avg_entry,
                    "mark": mark,
                    "market_value": pos.quantity * mark,
                    "unrealized_pnl": pos.quantity * (mark - pos.avg_entry),
                }
            )
        return pd.DataFrame(rows)

    def mark_to_market(self, prices: dict[str, float], as_of: datetime) -> dict:
        today = as_of.strftime("%Y-%m-%d")
        equity = self.state.cash + sum(pos.quantity * prices.get(ticker, pos.avg_entry) for ticker, pos in self.state.positions.items())
        if self.state.current_day != today:
            self.state.current_day = today
            self.state.day_start_equity = equity
            self.state.kill_switch_active = False
        intraday_drawdown = 0.0 if self.state.day_start_equity <= 0 else max(0.0, 1 - equity / self.state.day_start_equity)
        if intraday_drawdown + 1e-9 >= self.settings.risk.daily_drawdown_kill_switch:
            self.state.kill_switch_active = True
        gross_exposure = sum(abs(pos.quantity * prices.get(ticker, pos.avg_entry)) for ticker, pos in self.state.positions.items())
        metrics = {
            "equity": equity,
            "cash": self.state.cash,
            "gross_exposure": gross_exposure,
            "gross_exposure_pct": gross_exposure / equity if equity else 0.0,
            "intraday_drawdown": intraday_drawdown,
            "kill_switch_active": self.state.kill_switch_active,
            "realized_pnl": self.state.realized_pnl,
        }
        self.save()
        return metrics

    def apply_signals(self, candidates: pd.DataFrame, as_of: datetime) -> list[dict]:
        prices = dict(zip(candidates["ticker"], candidates["close"]))
        metrics = self.mark_to_market(prices, as_of)
        actions: list[dict] = []
        equity = metrics["equity"]
        for _, row in candidates.iterrows():
            action = row.get("action", "HOLD")
            ticker = row["ticker"]
            if action == "CONSIDER ENTRY":
                if self.state.kill_switch_active or row.get("risk_blocked", False):
                    continue
                position_budget = equity * self.settings.risk.max_position_pct
                target_budget = min(
                    position_budget,
                    equity * self.settings.risk.max_gross_exposure_pct - metrics["gross_exposure"],
                )
                if target_budget <= 0:
                    continue
                vol = max(float(row.get("forecast_vol", row.get("rv_20d", 0.25)) or 0.25), 0.05)
                scaled_budget = min(target_budget, position_budget / vol)
                qty = round(scaled_budget / max(float(row["close"]), 0.01), 4)
                if qty <= 0:
                    continue
                existing = self.state.positions.get(ticker)
                if existing is None:
                    self.state.positions[ticker] = Position(ticker=ticker, quantity=qty, avg_entry=float(row["close"]))
                self.state.cash -= qty * float(row["close"])
                actions.append({"ticker": ticker, "paper_action": "ENTRY", "qty": qty, "price": float(row["close"])})
            elif action in {"CONSIDER EXIT", "EXIT"} and ticker in self.state.positions:
                pos = self.state.positions.pop(ticker)
                proceeds = pos.quantity * float(row["close"])
                self.state.cash += proceeds
                self.state.realized_pnl += proceeds - pos.quantity * pos.avg_entry
                actions.append({"ticker": ticker, "paper_action": "EXIT", "qty": pos.quantity, "price": float(row["close"])})
        self.save()
        return actions
