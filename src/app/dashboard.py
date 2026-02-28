from __future__ import annotations

import json
import sys
from pathlib import Path
import os

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    import streamlit as st
except Exception:  # pragma: no cover
    st = None

from src.config import get_settings
from src.data.market_data import MarketDataAdapter
from src.pipelines.common import PipelineArtifacts, build_pipeline_artifacts, build_tracking_snapshot
from src.portfolio.paper_portfolio import PaperPortfolio
from src.state.store import SharedStateStore


if st is not None:  # pragma: no branch
    st.set_page_config(
        page_title="Stock Screening Agent",
        page_icon="ST",
        layout="wide",
    )


def _load_snapshot_impl() -> dict:
    _apply_streamlit_secret_env()
    settings = get_settings()
    store = SharedStateStore(settings)
    shared_snapshot = store.read_json("latest_snapshot", None)
    hourly_state = store.read_json("hourly_state", {"deltas": [], "as_of": None})
    if shared_snapshot:
        shared_snapshot["hourly_state"] = hourly_state
        return shared_snapshot
    artifacts = build_pipeline_artifacts(settings)
    portfolio = PaperPortfolio(settings)
    snapshot = build_dashboard_snapshot(artifacts, portfolio)
    snapshot["hourly_state"] = hourly_state
    return snapshot


if st is not None:
    load_snapshot = st.cache_data(ttl=900, show_spinner=False)(_load_snapshot_impl)
else:
    load_snapshot = _load_snapshot_impl


def _apply_streamlit_secret_env() -> None:
    if st is None:
        return
    for key in ["APP_USERNAME", "APP_PASSWORD", "GITHUB_STATE_REPO", "GITHUB_STATE_BRANCH", "GITHUB_STATE_TOKEN"]:
        try:
            value = st.secrets.get(key)
        except Exception:
            value = None
        if value:
            os.environ[key] = str(value)


def get_app_credentials() -> tuple[str, str]:
    username = os.getenv("APP_USERNAME", "")
    password = os.getenv("APP_PASSWORD", "")
    if st is not None:
        try:
            username = st.secrets.get("APP_USERNAME", username)
            password = st.secrets.get("APP_PASSWORD", password)
        except Exception:
            pass
    return username, password


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(15,118,110,0.16), transparent 30%),
                radial-gradient(circle at top right, rgba(217,119,6,0.14), transparent 25%),
                linear-gradient(180deg, #f7f2e8 0%, #f3eee3 100%);
        }
        .hero {
            padding: 1.4rem 1.6rem;
            border-radius: 20px;
            background: linear-gradient(135deg, rgba(15,118,110,0.94), rgba(17,24,39,0.92));
            color: #f8fafc;
            box-shadow: 0 20px 50px rgba(15, 23, 42, 0.18);
            margin-bottom: 1rem;
        }
        .hero h1 {
            font-size: 2rem;
            margin: 0 0 0.35rem 0;
        }
        .hero p {
            margin: 0;
            opacity: 0.9;
        }
        .nav-card {
            background: rgba(255, 255, 255, 0.72);
            border: 1px solid rgba(15, 23, 42, 0.06);
            border-radius: 18px;
            padding: 0.9rem 1rem;
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
            min-height: 140px;
        }
        .section-card {
            background: rgba(255, 253, 248, 0.92);
            border: 1px solid rgba(15, 23, 42, 0.08);
            border-radius: 18px;
            padding: 1rem 1rem 0.8rem 1rem;
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
        }
        .watch-card {
            background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(248,250,252,0.96));
            border: 1px solid rgba(15, 118, 110, 0.10);
            border-radius: 18px;
            padding: 1rem 1rem 0.7rem 1rem;
            margin-bottom: 0.85rem;
        }
        .pill {
            display: inline-block;
            padding: 0.2rem 0.55rem;
            margin-right: 0.4rem;
            border-radius: 999px;
            font-size: 0.8rem;
            background: #e6fffb;
            color: #115e59;
            border: 1px solid rgba(15,118,110,0.18);
        }
        .risk-pill {
            background: #fff7ed;
            color: #9a3412;
            border: 1px solid rgba(234,88,12,0.18);
        }
        .small-label {
            font-size: 0.8rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            color: #6b7280;
        }
        .guide-copy {
            color: #475569;
            font-size: 0.95rem;
            line-height: 1.5;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def require_login() -> None:
    username, password = get_app_credentials()
    if not username or not password:
        return

    if st.session_state.get("authenticated", False):
        return

    st.markdown(
        """
        <div class="hero">
            <h1>Research Console Login</h1>
            <p>Use your dashboard credentials to access recommendations, portfolio state, and risk alerts.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.form("login_form"):
        submitted_user = st.text_input("Username")
        submitted_pass = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
    if submitted and submitted_user == username and submitted_pass == password:
        st.session_state["authenticated"] = True
        st.rerun()
    if submitted:
        st.error("Invalid username or password.")
    st.stop()


def build_dashboard_snapshot(artifacts: PipelineArtifacts, portfolio: PaperPortfolio) -> dict:
    return build_tracking_snapshot(artifacts, portfolio)


def _normalize_snapshot(snapshot: dict) -> dict:
    recommendations = pd.DataFrame(snapshot.get("recommendations", []))
    watchlist = pd.DataFrame(snapshot.get("watchlist", []))

    if not recommendations.empty:
        if "conviction_label" not in recommendations.columns:
            recommendations["conviction_label"] = "Developing"
        if "opportunity_score" not in recommendations.columns:
            recommendations["opportunity_score"] = recommendations.get("fused_confidence", 0)
        snapshot["recommendations"] = recommendations.to_dict(orient="records")

    if not watchlist.empty:
        if "conviction_label" not in watchlist.columns:
            watchlist["conviction_label"] = "Developing"
        if "opportunity_score" not in watchlist.columns:
            watchlist["opportunity_score"] = watchlist.get("fused_confidence", 0)
        if "hold_horizon" not in watchlist.columns:
            watchlist["hold_horizon"] = "1-5 days"
        snapshot["watchlist"] = watchlist.to_dict(orient="records")

    snapshot.setdefault("hourly_state", {"deltas": [], "as_of": None})
    return snapshot


def _column_guide() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"column": "action", "meaning": "Suggested next step from the paper-trading engine.", "values": "CONSIDER ENTRY, WATCH, HOLD, CONSIDER EXIT"},
            {"column": "conviction_label", "meaning": "How strong the combined model and news setup is.", "values": "Low, Developing, Strong, High"},
            {"column": "opportunity_score", "meaning": "Overall ranking score balancing edge, catalyst strength, liquidity, and risk penalties.", "values": "Higher is better"},
            {"column": "fused_confidence", "meaning": "Ensemble confidence after blending factor, time-series, baseline, and event signals.", "values": "0% to 100%"},
            {"column": "risk_label", "meaning": "Current risk block status for new paper entries.", "values": "OK, RISKY"},
            {"column": "hold_horizon", "meaning": "Estimated paper-trade holding period based on catalyst type, conviction, and volatility regime.", "values": "1-3 days, 1-5 days, 3-10 days"},
            {"column": "invalidation_price", "meaning": "Price level that weakens the setup enough to stop respecting the current thesis.", "values": "Price threshold"},
            {"column": "catalyst", "meaning": "Most relevant event/news driver attached to the stock right now.", "values": "earnings, analyst action, company news, macro shock, geopolitical shock"},
            {"column": "xsec_score", "meaning": "Cross-sectional factor score versus the rest of the universe after neutralization.", "values": "Higher positive is stronger"},
            {"column": "ts_score", "meaning": "Time-series directional model view for that ticker alone.", "values": "Positive favors upside"},
            {"column": "vol_risk_score", "meaning": "Volatility/risk desk score used for sizing and risk blocks.", "values": "Lower is calmer, higher is hotter"},
        ]
    )


def _value_footnotes() -> list[str]:
    return [
        "`CONSIDER ENTRY`: the model stack sees a favorable paper-trade setup and the ticker is not risk-blocked.",
        "`WATCH`: interesting name, but not strong enough or not safe enough to size yet.",
        "`HOLD`: keep tracking an existing paper position or stay patient if no fresh edge is present.",
        "`CONSIDER EXIT`: thesis weakened, invalidation hit, or risk controls now override the setup.",
        "`Low` conviction: weak edge or conflicting signals.",
        "`Developing` conviction: setup is improving but not yet decisive.",
        "`Strong` conviction: multiple model families and/or news agree.",
        "`High` conviction: strongest current names after risk penalties.",
        "`RISKY`: new entries are blocked today even if the name still looks interesting.",
    ]


def _build_price_chart_frame(snapshot: dict, tickers: list[str]) -> pd.DataFrame:
    settings = get_settings()
    market = MarketDataAdapter(settings)
    selected = [ticker for ticker in tickers if ticker]
    if not selected:
        return pd.DataFrame()
    history = market.fetch_daily_history(selected, lookback_days=60)
    if history.empty:
        return pd.DataFrame()
    chart = history[history["ticker"].isin(selected)][["date", "ticker", "close"]].copy()
    chart["date"] = pd.to_datetime(chart["date"])
    return chart.pivot_table(index="date", columns="ticker", values="close").sort_index()


def _portfolio_view(snapshot: dict) -> pd.DataFrame:
    positions_df = pd.DataFrame(snapshot.get("positions", []))
    recommendations_df = pd.DataFrame(snapshot.get("recommendations", []))
    if positions_df.empty:
        return positions_df
    positions_df = positions_df.copy()
    positions_df["pnl_pct"] = ((positions_df["mark"] / positions_df["avg_entry"]) - 1).fillna(0.0)
    if not recommendations_df.empty:
        merge_cols = ["ticker", "action", "conviction_label", "hold_horizon", "risk_label", "invalidation_price"]
        positions_df = positions_df.merge(recommendations_df[merge_cols], on="ticker", how="left")
    return positions_df.sort_values("unrealized_pnl", ascending=False)


def render_app(snapshot: dict) -> None:
    if st is None:  # pragma: no cover
        raise RuntimeError("streamlit is required to render the dashboard. Install requirements.txt first.")
    snapshot = _normalize_snapshot(snapshot)
    inject_styles()
    require_login()

    st.markdown(
        f"""
        <div class="hero">
            <h1>Institutional Research Console</h1>
            <p>Systematic volatility screening, recommendation tracking, risk governance, and paper portfolio oversight.</p>
            <p><span class="small-label">Snapshot</span> {snapshot['as_of']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    control_col1, control_col2 = st.columns([1, 4])
    with control_col1:
        if st.button("Refresh State", use_container_width=True):
            load_snapshot.clear()
            st.rerun()
    with control_col2:
        st.caption("Refresh State reloads the latest shared snapshot from the repository state branch.")

    with st.expander("Manage My Holdings"):
        st.caption("These paper holdings are shared with the scheduled jobs, so hourly emails can warn on names you are tracking.")
        positions_df = pd.DataFrame(snapshot.get("positions", []))
        if not positions_df.empty:
            st.dataframe(positions_df, use_container_width=True, hide_index=True)
        with st.form("add_position_form"):
            form_cols = st.columns(3)
            ticker = form_cols[0].text_input("Ticker", "")
            quantity = form_cols[1].number_input("Quantity", min_value=0.0, value=0.0, step=1.0)
            avg_entry = form_cols[2].number_input("Average Entry", min_value=0.0, value=0.0, step=0.01)
            submitted = st.form_submit_button("Save Position")
            if submitted and ticker:
                settings = get_settings()
                portfolio = PaperPortfolio(settings)
                portfolio.upsert_position(ticker, quantity, avg_entry)
                load_snapshot.clear()
                st.rerun()
        remove_ticker = st.text_input("Remove Ticker", "")
        if st.button("Remove Position", use_container_width=False) and remove_ticker:
            settings = get_settings()
            portfolio = PaperPortfolio(settings)
            portfolio.remove_position(remove_ticker)
            load_snapshot.clear()
            st.rerun()

    market = snapshot["market_context"]
    portfolio_metrics = snapshot["portfolio_metrics"]
    portfolio_state = snapshot["portfolio_state"]
    hourly_state = snapshot.get("hourly_state", {"deltas": [], "as_of": None})
    column_guide = _column_guide()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("SPY 1d", f"{market['spy_ret_1d']:+.2%}")
    col2.metric("QQQ 1d", f"{market['qqq_ret_1d']:+.2%}")
    col3.metric("Equity", f"${portfolio_metrics['equity']:.2f}")
    col4.metric("Intraday DD", f"{portfolio_metrics['intraday_drawdown']:.2%}")
    col5.metric("Gross Exposure", f"{portfolio_metrics['gross_exposure_pct']:.2%}")

    recommendations_df = pd.DataFrame(snapshot["recommendations"])
    watchlist_df = pd.DataFrame(snapshot["watchlist"])
    positions_df = _portfolio_view(snapshot)

    st.subheader("Start Here")
    guide_cols = st.columns(3)
    guide_cols[0].markdown(
        """
        <div class="nav-card">
            <div class="small-label">1. Best Ideas</div>
            <h3>Watchlist</h3>
            <p class="guide-copy">Start with the Watchlist tab. It shows the strongest setups ranked by model potential, catalyst quality, and tradability.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    guide_cols[1].markdown(
        """
        <div class="nav-card">
            <div class="small-label">2. Risk Check</div>
            <h3>Risk State</h3>
            <p class="guide-copy">Check whether the kill-switch is active and whether a stock is marked RISKY before acting on any idea.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    guide_cols[2].markdown(
        """
        <div class="nav-card">
            <div class="small-label">3. What Changed</div>
            <h3>Hourly Deltas</h3>
            <p class="guide-copy">Use the hourly changes panel to see only what materially moved since the last update.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    status_left, status_right = st.columns([2, 3])
    with status_left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Risk State")
        st.markdown(f'<span class="pill">{market["risk_regime"]}</span>', unsafe_allow_html=True)
        if portfolio_state["kill_switch_active"]:
            st.markdown('<span class="pill risk-pill">Kill-switch active</span>', unsafe_allow_html=True)
        st.write(f"Cash: `${portfolio_state['cash']:.2f}`")
        st.write(f"Realized P&L: `${portfolio_state['realized_pnl']:.2f}`")
        st.write(f"Day-start equity: `${portfolio_state['day_start_equity']:.2f}`")
        st.markdown("</div>", unsafe_allow_html=True)
    with status_right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Latest Paper Actions")
        if snapshot["paper_actions"]:
            st.dataframe(pd.DataFrame(snapshot["paper_actions"]), use_container_width=True, hide_index=True)
        else:
            st.write("No new paper actions in the latest cycle.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("Latest Hourly Deltas")
    if hourly_state.get("deltas"):
        st.caption(f"Last hourly update: {hourly_state.get('as_of')}")
        st.dataframe(pd.DataFrame(hourly_state["deltas"]), use_container_width=True, hide_index=True)
    else:
        st.write("No persisted hourly deltas yet.")

    best_idea = watchlist_df.head(1)
    if not best_idea.empty:
        top = best_idea.iloc[0]
        st.markdown(
            f"""
            <div class="watch-card">
                <div class="small-label">Top Idea Right Now</div>
                <h3 style="margin-bottom:0.2rem;">{top['ticker']} · {top['action']}</h3>
                <p class="guide-copy">Conviction: <strong>{top.get('conviction_label', 'n/a')}</strong> | Opportunity score: <strong>{top.get('opportunity_score', 0):.2f}</strong> | Risk: <strong>{top['risk_label']}</strong></p>
                <p class="guide-copy">{top['why']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    tabs = st.tabs(["Overview", "Best Setups", "All Ideas", "Portfolio", "Model Governance", "Raw Snapshot"])

    with tabs[0]:
        st.subheader("Beginner Overview")
        overview_cols = st.columns(3)
        overview_cols[0].metric("Ideas on Watchlist", len(watchlist_df))
        overview_cols[1].metric("High Conviction Names", int((recommendations_df["conviction_label"] == "High").sum()))
        overview_cols[2].metric("News-Driven Names", int((recommendations_df["catalyst"].fillna("") != "").sum()))
        st.markdown(
            """
            **How to use this page**

            - Start with `Best Setups` for the clearest ideas.
            - Use `All Ideas` if you want to filter by ticker, risk, or action.
            - Ignore `Model Governance` unless you want the technical details.
            """,
        )
        with st.expander("Field Guide"):
            st.caption("Use this as a footnote reference when the app uses model language.")
            st.dataframe(column_guide, use_container_width=True, hide_index=True)
            for note in _value_footnotes():
                st.markdown(f"- {note}")
        if hourly_state.get("deltas"):
            st.markdown("**Latest notable changes**")
            st.dataframe(pd.DataFrame(hourly_state["deltas"]).head(5), use_container_width=True, hide_index=True)

    with tabs[1]:
        st.subheader("Best Setups")
        chart_names = watchlist_df["ticker"].head(5).tolist() if not watchlist_df.empty else []
        selected_chart_names = st.multiselect(
            "Time-Series Plot",
            options=watchlist_df["ticker"].tolist(),
            default=chart_names,
            help="Plot recent daily closes for the recommended names you want to compare.",
        )
        chart_frame = _build_price_chart_frame(snapshot, selected_chart_names)
        if not chart_frame.empty:
            st.line_chart(chart_frame, use_container_width=True)
        if watchlist_df.empty:
            st.write("No watchlist names available.")
        else:
            for row in watchlist_df.to_dict(orient="records"):
                st.markdown(
                    f"""
                    <div class="watch-card">
                        <div>
                            <span class="pill">{row['action']}</span>
                            <span class="pill">{row.get('conviction_label', 'n/a')}</span>
                            <span class="pill risk-pill">{row['risk_label']}</span>
                        </div>
                        <h3 style="margin-bottom:0.3rem;">{row['ticker']} · {row.get('sector', 'Other')}</h3>
                        <p class="guide-copy"><strong>Opportunity score:</strong> {row.get('opportunity_score', 0):.2f} | <strong>Hold horizon:</strong> {row.get('hold_horizon', '1-5 days')}</p>
                        <p style="margin-bottom:0.5rem;">{row['why']}</p>
                        <p><strong>Invalidation:</strong> {row['invalidation_text']}</p>
                        <p><strong>What changes:</strong> {row['what_changes']}</p>
                        <p><strong>Caveats:</strong> {row['caveats']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with tabs[2]:
        st.subheader("All Ideas")
        filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([1.2, 1.2, 1.2, 2])
        actions = ["All"] + sorted(recommendations_df["action"].dropna().unique().tolist())
        selected_action = filter_col1.selectbox("Action", actions, index=0)
        risk_options = ["All"] + sorted(recommendations_df["risk_label"].dropna().unique().tolist())
        selected_risk = filter_col2.selectbox("Risk", risk_options, index=0)
        conviction_options = ["All"] + sorted(recommendations_df["conviction_label"].dropna().unique().tolist())
        selected_conviction = filter_col3.selectbox("Conviction", conviction_options, index=0)
        search = filter_col4.text_input("Ticker Search", "")
        filtered = recommendations_df.copy()
        if selected_action != "All":
            filtered = filtered[filtered["action"] == selected_action]
        if selected_risk != "All":
            filtered = filtered[filtered["risk_label"] == selected_risk]
        if selected_conviction != "All":
            filtered = filtered[filtered["conviction_label"] == selected_conviction]
        if search:
            filtered = filtered[filtered["ticker"].str.contains(search.upper(), na=False)]
        filtered = filtered.sort_values(["opportunity_score", "fused_confidence"], ascending=[False, False])
        st.dataframe(
            filtered.rename(
                columns={
                    "close": "last_price",
                    "fused_confidence": "ensemble_confidence",
                    "xsec_score": "factor_score",
                    "ts_score": "time_series_score",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

    with tabs[3]:
        st.subheader("Paper Portfolio")
        st.caption("Refresh State or wait for the next hourly job to update marks, unrealized P&L, and exit warnings for these paper positions.")
        buy_cols = st.columns([1.4, 1, 1, 1])
        buy_ticker = buy_cols[0].selectbox(
            "Open / Update Paper Position",
            options=recommendations_df["ticker"].tolist() if not recommendations_df.empty else [],
            index=0 if not recommendations_df.empty else None,
            help="This does not place a real trade. It just records a paper position inside the app.",
        )
        default_price = 0.0
        if buy_ticker and not recommendations_df.empty:
            current_row = recommendations_df[recommendations_df["ticker"] == buy_ticker].head(1)
            if not current_row.empty:
                default_price = float(current_row.iloc[0]["close"])
        buy_qty = buy_cols[1].number_input("Quantity", min_value=0.0, value=1.0, step=1.0, key="portfolio_buy_qty")
        buy_entry = buy_cols[2].number_input("Entry Price", min_value=0.0, value=float(default_price), step=0.01, key="portfolio_buy_entry")
        trigger_buy = buy_cols[3].button("Save Paper Trade", use_container_width=True)
        if trigger_buy and buy_ticker:
            settings = get_settings()
            portfolio = PaperPortfolio(settings)
            portfolio.upsert_position(buy_ticker, buy_qty, buy_entry)
            load_snapshot.clear()
            st.rerun()
        if positions_df.empty:
            st.write("No active paper positions.")
        else:
            st.dataframe(positions_df, use_container_width=True, hide_index=True)
            held_chart_names = st.multiselect(
                "Held Names Chart",
                options=positions_df["ticker"].tolist(),
                default=positions_df["ticker"].tolist()[:4],
                help="Track how your held paper positions have moved over recent sessions.",
            )
            held_chart = _build_price_chart_frame(snapshot, held_chart_names)
            if not held_chart.empty:
                st.line_chart(held_chart, use_container_width=True)
            pnl_cols = st.columns(3)
            pnl_cols[0].metric("Unrealized P&L", f"${positions_df['unrealized_pnl'].sum():.2f}")
            pnl_cols[1].metric("Held Names", int(len(positions_df)))
            pnl_cols[2].metric("Avg Held Return", f"{positions_df['pnl_pct'].mean():+.2%}")
        st.json(portfolio_state)

    with tabs[4]:
        st.subheader("Model Cards")
        model_cards = snapshot["model_cards"]
        governance_cols = st.columns(4)
        governance_cols[0].json(model_cards["factor"])
        governance_cols[1].json(model_cards["deep"])
        governance_cols[2].json(model_cards.get("explainability", {}))
        governance_cols[3].json(model_cards["governance"])

    with tabs[5]:
        st.subheader("Raw Snapshot")
        st.code(json.dumps(snapshot, indent=2, default=str), language="json")


def main() -> None:
    snapshot = load_snapshot()
    render_app(snapshot)


if __name__ == "__main__":
    main()
