# Data Dictionary

> **MVP 0.1** — TASK-002 sample schemas plus TASK-005 candidate fields for future real MO data.  
> Sample CSV is **not** the final production format. Real data will use parquet under `data_store/`.

Timestamps in sample CSV use ISO-like strings (`YYYY-MM-DD HH:MM:SS`) and are parsed to `datetime64` on load.  
No real account data, API keys, or live feeds are stored in this repository.

---

## Part A — MVP Sample Schemas

Current loaders and tests use small simulated CSV fixtures under `data/sample/`.

### Option quote CSV

File: `data/sample/option_quotes_sample.csv`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `timestamp` | datetime | Yes | Quote time, e.g. `2025-01-02 09:31:00` |
| `underlying_symbol` | string | Yes | Underlying ticker, e.g. `IM` |
| `option_symbol` | string | Yes | Option contract code, e.g. `IM2501-C-5000` |
| `expiry` | date | Yes | Expiration date, `YYYY-MM-DD` |
| `strike` | float | Yes | Strike price |
| `option_type` | string | Yes | `C` (call) or `P` (put) |
| `bid_price` | float | Yes | Best bid |
| `ask_price` | float | Yes | Best ask |
| `last_price` | float | Yes | Last traded price |
| `volume` | int | Yes | Session volume |
| `open_interest` | int | Yes | Open interest |
| `underlying_price` | float | Yes | Underlying reference price at quote time |

**Quality rules:** `option_type` must be `C` or `P`; `bid_price` < `ask_price`; numeric price/strike fields; integer volume/OI; missing columns raise `ValueError` in the loader.

### Underlying quote CSV

File: `data/sample/underlying_quotes_sample.csv`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `timestamp` | datetime | Yes | Quote time, e.g. `2025-01-02 09:31:00` |
| `underlying_symbol` | string | Yes | Underlying ticker, e.g. `IM` |
| `last_price` | float | Yes | Last traded price |
| `bid_price` | float | Yes | Best bid |
| `ask_price` | float | Yes | Best ask |
| `volume` | int | Yes | Session volume |

**Quality rules:** `bid_price` < `ask_price`; numeric prices; integer volume; missing columns raise `ValueError` in the loader.

---

## Part B — MO Minute Quote Candidates

Future production path: `data_store/quotes/minute/MO/{symbol}/{trade_date}.parquet`  
Aligned from tick order book (design reference: legacy `Option_System_Research` data platform). **Not implemented in TASK-005.**

| Field | Type | Required now | Required future | Description |
|-------|------|--------------|-----------------|-------------|
| `target_time` | datetime | No | Yes | Standard minute slot (MO session grid) |
| `quote_time` | datetime | No | Yes | Source tick timestamp used for alignment |
| `quote_age_ms` | int | No | Yes | Delay from `target_time` to `quote_time` (ms) |
| `symbol` | string | No | Yes | Full contract code, e.g. `CFFEX.MO2601-C-6000` |
| `underlying_symbol` | string | No | Yes | Underlying / index reference |
| `expiry_date` | date | No | Yes | Contract expiration |
| `strike_price` | float | No | Yes | Strike |
| `option_type` | string | No | Yes | Call / put (normalize in TASK-006) |
| `bid_price1` | float | No | Yes | Best bid (level 1) |
| `ask_price1` | float | No | Yes | Best ask (level 1) |
| `bid_volume1` | int | No | Yes | Bid size |
| `ask_volume1` | int | No | Yes | Ask size |
| `last_price` | float | No | Optional | Last trade — not primary mark/IV input |
| `volume` | int | No | Optional | Session volume |
| `open_interest` | int | No | Optional | Open interest |
| `mid_price` | float | No | Yes | Midpoint when bid/ask valid |
| `micro_price` | float | No | Yes | Volume-weighted micro price |
| `spread_bps` | float | No | Yes | Bid-ask spread in bps |
| `price_source` | string | No | Yes | `micro`, `mid`, `last_inside_spread`, `last`, `none` |
| `quote_quality` | string | No | Yes | e.g. `ok`, `stale_quote`, `wide_spread`, `no_price` |

**Design rule:** prefer order book over last price for future mark/IV inputs.

---

## Part C — Contract Metadata Candidates

Future path: `data_store/contracts/MO/{trade_date}.parquet`

| Field | Type | Required now | Required future | Description |
|-------|------|--------------|-----------------|-------------|
| `symbol` | string | No | Yes | Option contract code |
| `underlying_symbol` | string | No | Yes | Underlying |
| `expiry_date` | date | No | Yes | Expiration |
| `strike_price` | float | No | Yes | Strike |
| `option_type` | string | No | Yes | Call / put |
| `term_role` | string | No | Yes | `current_month`, `next_month`, `current_quarter`, `next_quarter` |
| `contract_multiplier` | float | No | Yes | Contract size |
| `tick_size` | float | No | Yes | Minimum price increment |
| `list_date` | date | No | Optional | Listing date |
| `last_trade_date` | date | No | Optional | Last trading day |

Supporting cache (future): `data_store/contracts/MO/first_valid_dates.json`

---

## Part D — Four-Term Snapshot Candidates

Future path: `data_store/snapshots/four_term/MO/{trade_date}.parquet`  
Inherits bid/ask/micro/mid/quality fields from Part B.

| Field | Type | Required now | Required future | Description |
|-------|------|--------------|-----------------|-------------|
| `timestamp` | datetime | No | Yes | Standard minute (alias of `target_time`) |
| `term_role` | string | No | Yes | Four-term role |
| `futures_symbol` | string | No | Optional | Pricing forward instrument |
| `futures_price` | float | No | Optional | Forward/futures input for IV |
| `mark_price` | float | No | Future | Price used for IV/Greeks |
| `iv` | float | No | Deferred | Implied vol — post TASK-010 |
| `iv_quality` | string | No | Deferred | IV quality tag |
| `iv_method` | string | No | Deferred | `calc`, `interp`, `none` |

---

## Loader API

Current (TASK-002):

| Function | Input | Output |
|----------|-------|--------|
| `load_option_quotes(path)` | Option quote CSV path | `pandas.DataFrame` (Part A option columns) |
| `load_underlying_quotes(path)` | Underlying quote CSV path | `pandas.DataFrame` (Part A underlying columns) |

Loaders perform column checks and basic type coercion only. They do **not** compute Greeks, build option chains, or run backtests.

Future parquet loaders (TASK-006+) will be documented here when implemented.

---

## Schema Evolution Notes

| Topic | Decision |
|-------|----------|
| Sample vs production | Sample CSV stays for CI; production uses parquet in `data_store/` |
| Out of scope (current loaders) | Live feeds, tick/L2, databases, cleaning beyond coercion |
| Greeks / IV fields | Documented in Part D as deferred; not in data migration Phase 1 |
| Field naming | Production parquet uses snake_case English |
| Re-review gate | TASK-010 validates schema against first real MO samples |

See also: [data_store_design.md](data_store_design.md), [data_migration_plan.md](data_migration_plan.md).
