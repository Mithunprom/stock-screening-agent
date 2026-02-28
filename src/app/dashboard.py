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


def render_app(snapshot: dict) -> None:
    if st is None:  # pragma: no cover
        raise RuntimeError("streamlit is required to render the dashboard. Install requirements.txt first.")
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

    market = snapshot["market_context"]
    portfolio_metrics = snapshot["portfolio_metrics"]
    portfolio_state = snapshot["portfolio_state"]
    hourly_state = snapshot.get("hourly_state", {"deltas": [], "as_of": None})

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("SPY 1d", f"{market['spy_ret_1d']:+.2%}")
    col2.metric("QQQ 1d", f"{market['qqq_ret_1d']:+.2%}")
    col3.metric("Equity", f"${portfolio_metrics['equity']:.2f}")
    col4.metric("Intraday DD", f"{portfolio_metrics['intraday_drawdown']:.2%}")
    col5.metric("Gross Exposure", f"{portfolio_metrics['gross_exposure_pct']:.2%}")

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

    recommendations_df = pd.DataFrame(snapshot["recommendations"])
    watchlist_df = pd.DataFrame(snapshot["watchlist"])
    positions_df = pd.DataFrame(snapshot["positions"])

    tabs = st.tabs(["Recommendations", "Watchlist", "Portfolio", "Model Governance", "Raw Snapshot"])

    with tabs[0]:
        st.subheader("Recommendation Tracker")
        filter_col1, filter_col2, filter_col3 = st.columns([1.2, 1.2, 2])
        actions = ["All"] + sorted(recommendations_df["action"].dropna().unique().tolist())
        selected_action = filter_col1.selectbox("Action", actions, index=0)
        risk_options = ["All"] + sorted(recommendations_df["risk_label"].dropna().unique().tolist())
        selected_risk = filter_col2.selectbox("Risk", risk_options, index=0)
        search = filter_col3.text_input("Ticker Search", "")
        filtered = recommendations_df.copy()
        if selected_action != "All":
            filtered = filtered[filtered["action"] == selected_action]
        if selected_risk != "All":
            filtered = filtered[filtered["risk_label"] == selected_risk]
        if search:
            filtered = filtered[filtered["ticker"].str.contains(search.upper(), na=False)]
        st.dataframe(filtered, use_container_width=True, hide_index=True)

    with tabs[1]:
        st.subheader("Top Watchlist")
        if watchlist_df.empty:
            st.write("No watchlist names available.")
        else:
            for row in watchlist_df.to_dict(orient="records"):
                st.markdown(
                    f"""
                    <div class="watch-card">
                        <div>
                            <span class="pill">{row['action']}</span>
                            <span class="pill risk-pill">{row['risk_label']}</span>
                        </div>
                        <h3 style="margin-bottom:0.3rem;">{row['ticker']}</h3>
                        <p style="margin-bottom:0.5rem;">{row['why']}</p>
                        <p><strong>Invalidation:</strong> {row['invalidation_text']}</p>
                        <p><strong>What changes:</strong> {row['what_changes']}</p>
                        <p><strong>Caveats:</strong> {row['caveats']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with tabs[2]:
        st.subheader("Paper Portfolio")
        if positions_df.empty:
            st.write("No active paper positions.")
        else:
            st.dataframe(positions_df, use_container_width=True, hide_index=True)
        st.json(portfolio_state)

    with tabs[3]:
        st.subheader("Model Cards")
        model_cards = snapshot["model_cards"]
        governance_cols = st.columns(4)
        governance_cols[0].json(model_cards["factor"])
        governance_cols[1].json(model_cards["deep"])
        governance_cols[2].json(model_cards.get("explainability", {}))
        governance_cols[3].json(model_cards["governance"])

    with tabs[4]:
        st.subheader("Raw Snapshot")
        st.code(json.dumps(snapshot, indent=2, default=str), language="json")


def main() -> None:
    snapshot = load_snapshot()
    render_app(snapshot)


if __name__ == "__main__":
    main()
