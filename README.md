# Stock Screening + Research + Alerting Agent

Institutional-style, no-broker, no-auto-trading research product for US equities. The repo now contains:

- a Python research engine and scheduler
- a Python FastAPI service for low-latency market/news/signals/watchlist endpoints
- a premium Next.js frontend for dashboard, screener, ticker detail, watchlist, and paper portfolio UX
- API routes and sample-mode data so the product works without paid keys

## Scope and Safety

- No broker integrations
- No real order placement
- No auto-trading
- Outputs are limited to watchlists, forecasts, research, simulated paper actions, and risk alerts

## Features

- Daily 7:00 AM PT volatility screen with top 20 volatile US stocks over the last 5 trading days
- Hourly market-hours-only updates with signal deltas, invalidations, and risk freezes
- Modular market/news adapters with free-data defaults and graceful degradation
- Cross-sectional factor model, deep time-series forecaster, volatility model, news/event model, baseline gradient boosting model, and fused ensemble
- Paper portfolio starting with `$1000` cash
- Risk controls:
  - 10% intraday drawdown kill-switch
  - risky-ticker entry block
  - 20% max per ticker
  - 60% max gross exposure
  - ATR/volatility-based invalidations
- Walk-forward validation, model cards, drift/missingness checks
- SMTP email or dry-run console rendering

## Repository Layout

```text
web/
  src/app/
  src/components/
  src/lib/
src/
  config.py
  api_service/
  data/
  features/
  models/
  portfolio/
  alerts/
  pipelines/
  utils/
tests/
```

Architecture and workflow reference:

- [docs/WORKFLOW.md](/Users/mithunghosh/Documents/Stock_agent/codex%20stock%20agent/docs/WORKFLOW.md)

## Setup

### Python research engine

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Python API service

```bash
source .venv/bin/activate
python -m src.api_service
```

### Next.js product UI

```bash
cd web
npm install
cp .env.example .env.local
npm run dev
```

## Environment Variables

Required only for live email sending:

```bash
export SMTP_HOST=smtp.example.com
export SMTP_PORT=587
export SMTP_USER=user
export SMTP_PASS=pass
export EMAIL_FROM=alerts@example.com
export EMAIL_TO=you@example.com
```

Optional market/news providers:

```bash
export POLYGON_API_KEY=...
export ALPACA_API_KEY=...
export ALPACA_SECRET_KEY=...
```

Optional runtime controls:

```bash
export SCREENER_TIMEZONE=America/Los_Angeles
export SCREENER_STATE_DIR=.state
export SCREENER_CACHE_DIR=.cache
export SCREENER_MIN_AVG_DOLLAR_VOLUME=5000000
export SCREENER_MIN_PRICE=2
export SCREENER_MAX_POS_PCT=0.20
export SCREENER_MAX_GROSS_PCT=0.60
```

## Run

### Frontend

```bash
cd web
npm run dev
```

### FastAPI backend

```bash
source .venv/bin/activate
python -m src.api_service
```

Core product screens:

- `/` dashboard
- `/screener`
- `/ticker/[ticker]`
- `/watchlist`
- `/portfolio`
- `/account`
- `/pricing`
- `/login`

### API endpoints

The Next.js app exposes:

- `/api/dashboard`
- `/api/market/quote?ticker=AAPL`
- `/api/market/candles?ticker=AAPL&interval=1h&range=1M`
- `/api/screener/top-volatile?window=5d&limit=20`
- `/api/news/latest?tickers=AAPL,NVDA`
- `/api/signals/summary?ticker=AAPL`
- `/api/portfolio/state`
- `/api/watchlist`
- `/api/preferences`
- `/api/stream/updates?tickers=AAPL,NVDA,LMT`

The dedicated FastAPI service exposes the same paths under `http://localhost:8000/api/...`.

### Research jobs

Daily dry-run:

```bash
python -m src.pipelines.daily_job --dry-run
```

Hourly dry-run:

```bash
python -m src.pipelines.hourly_job --dry-run
```

Force the hourly job to render even outside market hours:

```bash
python -m src.pipelines.hourly_job --dry-run --force
```

## Scheduling

The app is timezone-aware in code. Cron itself is not holiday-aware, so schedule the jobs and let the pipeline exit on weekends and NYSE holidays.

### Cron examples

Daily at 7:00 AM America/Los_Angeles:

```cron
CRON_TZ=America/Los_Angeles
0 7 * * 1-5 cd /Users/mithunghosh/Documents/Stock_agent/codex\ stock\ agent && /usr/bin/env python -m src.pipelines.daily_job
```

Hourly during the NYSE session. Because NYSE runs 9:30 AM to 4:00 PM ET, the safe cron pattern is to run every hour on weekdays and let the calendar gate it:

```cron
CRON_TZ=America/New_York
0 9-16 * * 1-5 cd /Users/mithunghosh/Documents/Stock_agent/codex\ stock\ agent && /usr/bin/env python -m src.pipelines.hourly_job
```

Notes:

- The `09:00 ET` run will be skipped by the job because it is pre-open.
- The `16:00 ET` run is permitted and acts as the close-hour update.
- Market holidays and weekends are handled inside `src/data/calendar.py`.

If you want a stricter scheduler, use a workflow runner that supports calendars and timezones explicitly.

## Dry-run / Sample-mode Behavior

- If SMTP settings are missing or `--dry-run` is used, emails are printed to stdout.
- If market/news APIs are unavailable, the system falls back to cached data and then to deterministic sample data so the report still renders.
- The Next.js UI reads from `.state/shared/latest_snapshot.json` and falls back to deterministic sample data if no snapshot exists.
- Candlestick endpoints always degrade to deterministic sample candles when live intraday data is unavailable.
- Watchlist preferences are stored in `.state/shared/frontend_preferences.json`.

## Product UX Notes

- One candlestick chart per ticker detail page. No multi-ticker overlays.
- Watch / consider / invalidated language only. No broker connectivity, no real execution.
- Data health and model freshness are surfaced as trust markers.
- Alerts use per-ticker thresholds plus dedupe/cooldown logic driven by the watchlist preferences file.
- Session auth and billing pages are scaffolding only. They are intentionally non-broker, non-payment-integrated placeholders ready for a future auth/billing provider.

## Email Examples

### Hourly digest

```text
Subject: Hourly Update — 10:00 ET — Signals & Risk

## Status
Kill-switch active: False
Intraday drawdown: 1.40%
Gross exposure: 42.00%

## Material Changes
| ticker | fused_confidence | risk_label | action          | change_reason                            |
|:-------|:-----------------|:-----------|:----------------|:-----------------------------------------|
| LMT    | 74%              | OK         | CONSIDER ENTRY  | Defense tape + positive factor spread    |
| NVDA   | 69%              | OK         | WATCH           | Leadership sector + supportive analyst   |

Disclaimer: research only, not investment advice, no real trades are executed.
```

### Major catalyst alert

```text
Subject: Major Catalyst / Signal Alert — 11:00 ET

## Event-Driven Alerts
Only tracked tickers that crossed your configured thresholds are included below.

| ticker | action          | risk_label | fused_confidence | catalyst            | alert_reason                               |
|:-------|:----------------|:-----------|:-----------------|:--------------------|:-------------------------------------------|
| LMT    | CONSIDER ENTRY  | OK         | 74%              | geopolitical shock  | major catalyst: geopolitical shock, confidence delta 8% |

Disclaimer: research only, not investment advice, no real trades are executed.
```

## Free Hosting

Recommended default for the new UI: Vercel for `web/`, with the Python FastAPI service on Railway/Render/Fly.io and the research jobs continuing on GitHub Actions or another scheduler.

Why:

- clean fit for Next.js
- fast edge delivery
- straightforward preview deployments
- keeps UI and research APIs cleanly separated

Deployment steps:

1. Push this repo to GitHub.
2. Deploy `web/` on Vercel.
3. Deploy `src.api_service` on a Python host.
4. Set `NEXT_PUBLIC_API_BASE_URL` and `API_BASE_URL` in the frontend deployment.
5. Keep the Python hourly/daily workflows on GitHub Actions.
6. Point both layers at the same shared-state branch if you want the web UI to mirror the scheduler outputs.

Your repo is already on GitHub here:

- [stock-screening-agent](https://github.com/Mithunprom/stock-screening-agent)

Recommended deployment for cross-device access:

- Vercel hosts the Next.js UI
- FastAPI hosts the market/news/signals/watchlist service
- GitHub Actions runs the daily and hourly jobs
- SMTP sends the email alerts

This separation matters because Streamlit Cloud is good for serving the app, but it is not the right place to run market-hour schedulers.

## GitHub Actions Setup

The repo includes:

- [.github/workflows/daily_screen.yml](/Users/mithunghosh/Documents/Stock_agent/codex%20stock%20agent/.github/workflows/daily_screen.yml)
- [.github/workflows/hourly_update.yml](/Users/mithunghosh/Documents/Stock_agent/codex%20stock%20agent/.github/workflows/hourly_update.yml)

Add these GitHub repository secrets:

```text
SMTP_HOST
SMTP_PORT
SMTP_USER
SMTP_PASS
EMAIL_FROM
EMAIL_TO
APP_USERNAME
APP_PASSWORD
```

Then:

1. Go to the GitHub repo `Settings` > `Secrets and variables` > `Actions`
2. Add the secrets above
3. Open the `Actions` tab and enable workflows if GitHub asks
4. Run `Daily Screen` once with `workflow_dispatch`
5. Run `Hourly Update` once with `workflow_dispatch`

Notes:

- The hourly workflow now runs only in narrower UTC windows that correspond to the NYSE session instead of every weekday hour.
- The daily workflow now uses two seasonal schedules:
  - `15:00 UTC` for Pacific Standard Time months
  - `14:00 UTC` for Pacific Daylight Time months
- GitHub Actions cron is still month-based, not true timezone-aware scheduling, so the exact DST switchover weeks in March and November may need manual adjustment if you want perfect alignment.
- The Python pipeline still blocks weekends, holidays, pre-market, and post-market sends.
- The workflows publish `state/latest_snapshot.json` and `state/hourly_state.json` to the dedicated `state` branch using the built-in GitHub Actions token. The hosted Streamlit app reads those files, so the dashboard and schedulers share one persistent state without forcing a Streamlit redeploy on every hourly update.

Other free options:

- Hugging Face Spaces:
  use a Docker Space if you want to run Streamlit there
- Render:
  possible on the free tier, but free services may sleep and are not ideal for a monitoring app

References:

- [Vercel for Next.js](https://vercel.com/docs/frameworks/nextjs)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Hugging Face Streamlit Spaces note](https://huggingface.co/docs/hub/spaces-sdks-streamlit)
- [Render free services](https://render.com/docs/free)

## Risk Controls

- Daily drawdown kill-switch:
  - At market open, the paper portfolio stores day-start equity.
  - If intraday drawdown reaches or exceeds 10%, new paper entries are frozen for the remainder of that trading day.
  - Existing positions can still generate hold or consider-exit alerts.
- Extreme ticker risk block:
  - Blocks new entries for tickers with severe short-horizon downside or abnormal unstable activity.
- Sizing:
  - Max 20% of equity in one ticker
  - Max 60% gross exposure overall
  - Volatility-targeted sizing with caps
- Invalidations:
  - Default invalidation is `2 x ATR` from the reference level, adjusted for regime volatility

## Caveats

- `yfinance` intraday coverage and public RSS coverage are best-effort and can be delayed.
- The deep model uses PyTorch when available and falls back to a deterministic heuristic when unavailable.
- GARCH uses `arch` when available and falls back to EWMA volatility.
- FinBERT, SHAP, and boosted tree extras are optional. The code degrades without them.

## Testing

```bash
pytest -q
```

## Example Daily Email

See the example format in the section below or generate one with:

```bash
python -m src.pipelines.daily_job --dry-run
```

## Example Daily Email Output

```markdown
Subject: Daily Volatility Screen (Top 20) — 2026-02-28

## Market Context
SPY last: 588.21, 1d: +0.42%, 5d realized vol: 18.3%
QQQ last: 517.10, 1d: +0.77%, 5d realized vol: 22.1%
Risk regime: Elevated but tradeable

## Top 20 Volatility Screen
| Ticker | Last | 5d RV | ATR% | Avg $ Vol | Gap% | Catalyst | XSec | TS | Vol Risk | Fused | Risk |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|
| NVDA | 914.22 | 56.4% | 4.8% | 38.2B | 1.3% | AI demand / analyst action | 0.72 | 0.61 | 0.41 | 0.66 | B |
| SMCI | 910.18 | 63.8% | 6.1% | 9.4B | -0.8% | guidance / momentum | 0.66 | 0.58 | 0.56 | 0.60 | B |
...

## Watchlist Highlights

### NVDA — CONSIDER ENTRY
Why: strong 5d and 20d momentum, supportive news cluster, above-median liquidity, and positive fused signal with controlled risk.
Invalidation: close below 896.40 or approximately 2x ATR below the reference level.
What changes the view: negative earnings pre-announcement, semis sector reversal, or fused score falling below 0.50.
Caveats: elevated implied event sensitivity, public-feed news may lag.

### XOM — WATCH
Why: volatility remains high, but risk-adjusted reward is weaker than leaders and energy beta is doing more of the work than idiosyncratic alpha.
Invalidation: do not upgrade unless price reclaims the intraday trend and event-risk score falls.
What changes the view: crude shock, guidance, or factor score improvement.
Caveats: macro-driven tape.

Disclaimer: research only, not investment advice, no real trades are executed.
```
