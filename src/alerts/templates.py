from __future__ import annotations

from datetime import datetime

import pandas as pd

from src.utils.time import format_hour_et


def render_table(frame: pd.DataFrame, columns: list[str]) -> str:
    display = frame[columns].copy()
    for col in display.columns:
        if pd.api.types.is_float_dtype(display[col]):
            display[col] = display[col].map(lambda x: f"{x:.2f}" if pd.notna(x) else "")
    return display.to_markdown(index=False)


def render_daily_email(as_of: datetime, market_context: dict, screen: pd.DataFrame, watchlist: pd.DataFrame) -> tuple[str, str]:
    subject = f"Daily Opportunity + Catalyst Screen (Top 20) — {as_of:%Y-%m-%d}"
    top_pick = watchlist.head(1)
    lines = [
        "## Market Context",
        f"SPY last: {market_context.get('spy_last', 0):.2f}, 1d: {market_context.get('spy_ret_1d', 0):+.2%}, 5d realized vol: {market_context.get('spy_rv_5d', 0):.1%}",
        f"QQQ last: {market_context.get('qqq_last', 0):.2f}, 1d: {market_context.get('qqq_ret_1d', 0):+.2%}, 5d realized vol: {market_context.get('qqq_rv_5d', 0):.1%}",
        f"Risk regime: {market_context.get('risk_regime', 'Moderate')}",
        "",
    ]
    if not top_pick.empty:
        row = top_pick.iloc[0]
        lines.extend(
            [
                "## Top Pick of the Day",
                f"**{row['ticker']} — {row['action']}**",
                f"Why this is the single best setup right now: {row['why']}",
                f"Invalidation: {row['invalidation_text']}",
                f"What would change the view: {row['what_changes']}",
                "",
            ]
        )
    lines.extend(
        [
        "## Top 20 Opportunity Screen",
        render_table(
            screen,
            [
                "ticker",
                "sector",
                "close",
                "catalyst",
                "opportunity_score",
                "conviction_label",
                "fused_confidence",
                "xsec_score",
                "ts_score",
                "vol_risk_score",
                "risk_label",
            ],
        ),
        "",
        "## Watchlist Highlights",
        ]
    )
    for _, row in watchlist.iterrows():
        lines.extend(
            [
                f"### {row['ticker']} — {row['action']}",
                f"Why: {row['why']}",
                f"Setup quality: conviction {row.get('conviction_label', 'n/a')}, opportunity score {row.get('opportunity_score', 0):.2f}, fused confidence {row.get('fused_confidence', 0):.2f}.",
                f"Invalidation: {row['invalidation_text']}",
                f"What changes the view: {row['what_changes']}",
                f"Caveats: {row['caveats']}",
                "",
            ]
        )
    lines.append("Disclaimer: research only, not investment advice, no real trades are executed.")
    return subject, "\n".join(lines)


def render_hourly_email(as_of: datetime, deltas: pd.DataFrame, risk_summary: dict) -> tuple[str, str]:
    subject = f"Hourly Update — {format_hour_et(as_of)} — Signals & Risk"
    lines = [
        "## Status",
        f"Kill-switch active: {risk_summary.get('kill_switch_active', False)}",
        f"Intraday drawdown: {risk_summary.get('intraday_drawdown', 0):.2%}",
        f"Gross exposure: {risk_summary.get('gross_exposure_pct', 0):.2%}",
        "",
        "## Material Changes",
    ]
    if deltas.empty:
        lines.append("No material signal deltas this hour.")
    else:
        lines.append(
            render_table(
                deltas,
                ["ticker", "fused_confidence", "risk_label", "action", "change_reason"],
            )
        )
    lines.append("")
    lines.append("Disclaimer: research only, not investment advice, no real trades are executed.")
    return subject, "\n".join(lines)
