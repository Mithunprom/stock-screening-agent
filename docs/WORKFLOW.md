# App Workflow

This document describes the current end-to-end workflow of the stock screening, research, alerting, and dashboard system.

## 1. System Purpose

The system does not place trades. It:

- screens US equities for volatility and opportunity
- produces model-based research signals
- sends daily and hourly emails
- maintains a paper portfolio
- publishes shared state for the hosted dashboard

## 2. High-Level Components

- `src/data/`
  - market data adapter
  - news adapter
  - market calendar
  - sector map
- `src/features/`
  - universe filtering
  - feature engineering
  - volatility metrics
- `src/models/`
  - factor model
  - time-series model
  - volatility model
  - baseline model
  - fusion model
  - explainability
  - validation
- `src/portfolio/`
  - paper portfolio
  - execution rules
  - risk engine
- `src/alerts/`
  - email rendering
  - SMTP sending
- `src/state/`
  - shared state storage
- `src/pipelines/`
  - daily job
  - hourly job
- `src/app/`
  - Streamlit dashboard

## 3. Data Flow

### Market Data

Source order:

1. `yfinance` if enabled and available
2. cached local data if present
3. deterministic synthetic fallback data

Files:

- `src/data/market_data.py`

### News Data

Source order:

1. public RSS feeds
2. heuristic fallback sample news

Sentiment:

1. FinBERT if enabled and available
2. heuristic lexicon fallback

Files:

- `src/data/news_data.py`

### Calendar

Source order:

1. `pandas_market_calendars` if available
2. NYSE holiday fallback logic

Files:

- `src/data/calendar.py`

## 4. Universe Construction

The pipeline starts from a configured list of liquid US tickers and ETFs.

Filters:

- minimum price
- minimum average dollar volume
- minimum listing history

Files:

- `src/features/universe.py`
- `src/config.py`

## 5. Feature Engineering

Built features include:

- `ret_1d`, `ret_5d`, `ret_20d`
- reversal
- `rv_5d`, `rv_20d`
- ATR and ATR percent
- gap percent
- dollar volume and rolling average dollar volume
- beta proxies vs `SPY` and `QQQ`
- intraday 1h return and intraday realized volatility
- sector membership
- sector-relative momentum

Files:

- `src/features/build_features.py`
- `src/features/volatility.py`
- `src/data/sector_map.py`

## 6. Model Stack

### A. Cross-Sectional Factor Model

File:

- `src/models/factor_model.py`

What it does:

- builds a daily cross-sectional score
- uses walk-forward splits
- fits feature weights from historical rank correlation
- neutralizes against market beta proxies
- neutralizes by sector using sector dummy variables

Validation:

- IC
- IC IR
- turnover
- gross long-short return
- net long-short return
- average trading cost in bps
- hit rate

### B. Time-Series Forecasting Model

File:

- `src/models/deep_model.py`

What it does:

- if PyTorch is enabled, uses an LSTM forecaster with MC-dropout style uncertainty
- otherwise uses a walk-forward heuristic time-series score

Outputs:

- `ts_score`
- `ts_uncertainty`

Validation metadata:

- backend used
- directional accuracy
- MAE

### C. Volatility Model

File:

- `src/models/vol_model.py`

What it does:

- uses GARCH(1,1) if `arch` is available
- otherwise falls back to EWMA volatility

Outputs:

- forward volatility estimate
- volatility risk score

### D. Baseline Model

File:

- `src/models/baseline_model.py`

What it does:

- if enabled, uses calibrated `HistGradientBoostingClassifier`
- otherwise uses a deterministic heuristic baseline score
- uses walk-forward prediction logic

Outputs:

- `baseline_score`
- `baseline_probability`

Validation:

- same validation engine as factor ranking evaluation

### E. News / Event Model

File:

- `src/data/news_data.py`

What it does:

- collects public headlines
- deduplicates by clustered headline key
- scores sentiment
- tags catalysts
- computes:
  - sentiment
  - catalyst
  - event risk score
  - catalyst confidence
  - narrative summary

### F. Fusion

File:

- `src/models/fusion.py`

What it does:

- combines:
  - factor score
  - time-series score
  - baseline score
  - event score
  - volatility risk penalty
- produces:
  - fused score
  - fused confidence
  - risk grade

## 7. Validation Engine

File:

- `src/models/validation.py`

What it measures:

- Spearman IC
- IC IR
- turnover
- gross long-short return
- net long-short return
- average trading cost
- hit rate

Costs included:

- transaction cost bps
- slippage bps

This is a stronger walk-forward validation layer than the initial lightweight prototype, but it is still a research framework rather than a full institutional backtesting platform.

## 8. Risk and Portfolio Workflow

Files:

- `src/portfolio/risk.py`
- `src/portfolio/paper_portfolio.py`
- `src/portfolio/execution_rules.py`

### Risk Engine

Blocks new entries when:

- 1h return is too negative
- gap down is too large
- abnormal adverse volume is detected
- intraday realized volatility is extreme

### Paper Portfolio

Tracks:

- cash
- positions
- average entry
- realized P&L
- unrealized P&L
- gross exposure
- intraday drawdown

### Kill Switch

- at day start, the system stores day-start equity
- if intraday drawdown reaches 10% or worse
- new entries are frozen for the rest of that day
- existing positions remain tracked

## 9. Daily Pipeline

File:

- `src/pipelines/daily_job.py`

Steps:

1. load config
2. build pipeline artifacts
3. rank top volatility names
4. render daily email
5. send email
6. persist dashboard snapshot to shared state

Output:

- daily email
- `latest_snapshot.json`

## 10. Hourly Pipeline

File:

- `src/pipelines/hourly_job.py`

Steps:

1. load config
2. check market session
3. build pipeline artifacts
4. compare current state with prior hourly state
5. keep only material deltas
6. render hourly email
7. send email
8. persist hourly delta state
9. refresh shared dashboard snapshot

Outputs:

- hourly email
- `hourly_state.json`
- refreshed `latest_snapshot.json`

## 11. Shared State Workflow

File:

- `src/state/store.py`

Purpose:

- lets GitHub Actions and Streamlit read the same live snapshot

Storage behavior:

1. write local JSON under `.state/shared/`
2. if configured, write shared JSON to GitHub repository branch `state`
3. hosted Streamlit app reads from that branch

Shared state files:

- `state/latest_snapshot.json`
- `state/hourly_state.json`

## 12. Dashboard Workflow

File:

- `src/app/dashboard.py`

Behavior:

1. try reading `latest_snapshot.json` from shared state
2. try reading `hourly_state.json` from shared state
3. if unavailable, rebuild from local pipeline
4. render:
   - market summary
   - risk state
   - paper actions
   - latest hourly deltas
   - recommendation tracker
   - watchlist
   - portfolio
   - model governance
   - raw snapshot

Controls:

- login gate using app credentials
- refresh button to reload latest shared state

## 13. Automation Workflow

Files:

- `.github/workflows/daily_screen.yml`
- `.github/workflows/hourly_update.yml`

Behavior:

- `Daily Screen` runs on a seasonal UTC schedule approximating `7:00 AM PT`
- `Hourly Update` runs during narrower UTC windows mapped to NYSE hours
- both workflows can also be run manually from GitHub Actions

## 14. Hosted App Workflow

Hosted UI:

- Streamlit Community Cloud

Branching model:

- `main` hosts application code
- `state` stores live shared snapshots

Why:

- avoids redeploying the app every time shared state updates

## 15. Operational Checklist

To operate correctly, the system needs:

- Streamlit secrets:
  - `APP_USERNAME`
  - `APP_PASSWORD`
  - `GITHUB_STATE_REPO`
  - `GITHUB_STATE_BRANCH`
- GitHub Actions secrets:
  - `SMTP_HOST`
  - `SMTP_PORT`
  - `SMTP_USER`
  - `SMTP_PASS`
  - `EMAIL_FROM`
  - `EMAIL_TO`
  - `APP_USERNAME`
  - `APP_PASSWORD`

## 16. Current Limitations

- GitHub Actions cron is not truly timezone-aware
- DST transitions are approximated using month-based schedules
- public RSS sources are rate-limited and inconsistent
- FinBERT and SHAP are optional runtime upgrades, not guaranteed in every environment
- backtesting is stronger than the initial prototype but still not a full event-accurate institutional simulator
