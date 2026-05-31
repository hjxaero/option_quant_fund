# Data Dictionary

> **MVP 0.1** — TASK-002 sample schemas; TASK-006 formal `data_store` field contracts.  
> Sample CSV is **not** the final production format. Real MO data uses parquet under `data_store/`.

Timestamps: sample CSV uses `YYYY-MM-DD HH:MM:SS` strings; production uses `datetime64` in parquet.  
No real account data, API keys, or live feeds are stored in this repository.

Field contracts below are **documentation only** in TASK-006 — no parquet loaders yet.

---

## Part A — MVP Sample Schemas

Current loaders and tests use simulated CSV under `data/sample/`.

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

**Quality rules:** `option_type` ∈ {`C`, `P`}; `bid_price` < `ask_price`; missing columns → `ValueError`.

### Underlying quote CSV

File: `data/sample/underlying_quotes_sample.csv`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `timestamp` | datetime | Yes | Quote time |
| `underlying_symbol` | string | Yes | Underlying ticker |
| `last_price` | float | Yes | Last traded price |
| `bid_price` | float | Yes | Best bid |
| `ask_price` | float | Yes | Best ask |
| `volume` | int | Yes | Session volume |

---

## Part B — Minute Quotes (`data_store/quotes/minute/`)

Path: `data_store/quotes/minute/MO/{symbol}/{trade_date}.parquet`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `target_time` | datetime | Yes | Standard minute slot (MO session grid) |
| `quote_time` | datetime | Yes | Source tick timestamp used for alignment |
| `quote_age_ms` | int | Yes | `target_time − quote_time` in milliseconds |
| `symbol` | string | Yes | e.g. `CFFEX.MO2601-C-6000` |
| `product` | string | Yes | `MO` |
| `underlying_symbol` | string | Yes | Index / underlying reference |
| `expiry_date` | date | Yes | Contract expiration |
| `strike_price` | float | Yes | Strike |
| `option_type` | string | Yes | `call` or `put` (production enum) |
| `bid_price1` | float | Yes* | Best bid (*nullable if `quote_quality=no_price`) |
| `ask_price1` | float | Yes* | Best ask |
| `bid_volume1` | int | Optional | Bid size |
| `ask_volume1` | int | Optional | Ask size |
| `last_price` | float | Optional | Last trade — not primary mark input |
| `volume` | int | Optional | Session volume |
| `open_interest` | int | Optional | Open interest |
| `mid_price` | float | Optional | Midpoint when bid/ask valid |
| `micro_price` | float | Optional | Volume-weighted micro price |
| `spread_bps` | float | Optional | Bid-ask spread (bps) |
| `price_source` | string | Yes | `micro`, `mid`, `last_inside_spread`, `last`, `none` |
| `quote_quality` | string | Yes | `ok`, `stale_quote`, `wide_spread`, `no_price`, … |
| `schema_version` | string | Yes | Contract version, e.g. `v1` |

**Constraints:** `quote_age_ms` > 60000 → typically `stale_quote`; prefer order book over `last_price` for future mark/IV.

---

## Part C — Contracts (`data_store/contracts/`)

Path: `data_store/contracts/MO/{trade_date}.parquet`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `trade_date` | date | Yes | Trading session date |
| `product` | string | Yes | `MO` |
| `symbol` | string | Yes | Full contract code |
| `underlying_symbol` | string | Yes | Underlying |
| `expiry_date` | date | Yes | Expiration |
| `strike_price` | float | Yes | Strike |
| `option_type` | string | Yes | `call` or `put` |
| `term_role` | string | Optional | Four-term role when in universe |
| `contract_multiplier` | float | Yes | Contract size |
| `tick_size` | float | Yes | Minimum price increment |
| `list_date` | date | Optional | Listing date |
| `last_trade_date` | date | Optional | Last trading day |
| `schema_version` | string | Yes | e.g. `v1` |

**Four-term roles:** `current_month`, `next_month`, `current_quarter`, `next_quarter`

**Cache (JSON, optional):** `data_store/contracts/MO/first_valid_dates.json` — maps `symbol` → first date with usable quotes.

---

## Part D — Four-Term Snapshots (`data_store/snapshots/four_term/`)

Path: `data_store/snapshots/four_term/MO/{trade_date}.parquet`

Inherits Part B quote fields plus:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `timestamp` | datetime | Yes | Same as `target_time` |
| `term_role` | string | Yes | Four-term role for this row |
| `futures_symbol` | string | Optional | Pricing forward instrument |
| `futures_price` | float | Optional | Forward input for future IV |
| `mark_price` | float | Optional | Mark for IV/Greeks (future) |
| `iv` | float | Deferred | Implied vol — post TASK-010 |
| `iv_quality` | string | Deferred | IV quality tag |
| `iv_method` | string | Deferred | `calc`, `interp`, `none` |
| `schema_version` | string | Yes | e.g. `v1` |

**Completeness rule:** snapshot file exists only if all expected four-term minute files for that day pass quality gate (TASK-009+).

---

## Part E — Ticks (`data_store/ticks/`)

Path: `data_store/ticks/MO/{symbol}/{trade_date}.parquet`  
Optional layer; may be skipped if TASK-008 writes minute quotes directly from API.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `datetime` | datetime | Yes | Exchange tick timestamp |
| `symbol` | string | Yes | Contract code |
| `product` | string | Yes | `MO` |
| `last_price` | float | Optional | Last trade price |
| `volume` | int | Optional | Tick volume |
| `bid_price1` | float | Optional | Best bid |
| `ask_price1` | float | Optional | Best ask |
| `bid_volume1` | int | Optional | Bid size |
| `ask_volume1` | int | Optional | Ask size |
| `open_interest` | int | Optional | Open interest if provided |
| `schema_version` | string | Yes | e.g. `v1` |

---

## Part F — Quality State (`data_store/quality/`)

Path: `data_store/quality/MO/{symbol}/{trade_date}.state.json`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `product` | string | Yes | `MO` |
| `symbol` | string | Yes | Contract code |
| `trade_date` | string | Yes | `YYYY-MM-DD` |
| `rows` | int | Yes | Row count in parquet |
| `last_target_time` | string | Optional | ISO datetime of last minute slot |
| `last_quote_time` | string | Optional | ISO datetime of last source quote |
| `complete` | bool | Yes | Whether file passed completeness check |
| `updated_at` | string | Yes | ISO datetime of last write |
| `schema_version` | string | Yes | State file contract version |

**Batch summaries (optional):** `data_store/quality/MO/{batch_id}_summary.json` — aggregate ratios (`ok_ratio`, `missing_ratio`, …) from TASK-009.

---

## Enumerations (TASK-006)

| Enum | Values |
|------|--------|
| `option_type` (production) | `call`, `put` |
| `option_type` (sample CSV) | `C`, `P` (loaders map in TASK-010 if needed) |
| `term_role` | `current_month`, `next_month`, `current_quarter`, `next_quarter` |
| `price_source` | `micro`, `mid`, `last_inside_spread`, `last`, `none` |
| `quote_quality` | `ok`, `wide_spread`, `stale_quote`, `no_price`, `invalid_bid_ask`, `crossed_market`, `low_liquidity` |

---

## Loader API

**Current (TASK-002)** — sample CSV only:

| Function | Input | Output |
|----------|-------|--------|
| `load_option_quotes(path)` | Sample CSV path | DataFrame (Part A) |
| `load_underlying_quotes(path)` | Sample CSV path | DataFrame (Part A) |

**Future (TASK-007+):** parquet readers for Parts B–F — not implemented in TASK-006.

Loaders do **not** compute Greeks, build option chains, or run backtests.

---

## Schema Evolution Notes

| Topic | Decision |
|-------|----------|
| Sample vs production | Sample CSV for CI; production parquet in `data_store/` |
| Mapping sample → production | `C`/`P` → `call`/`put`; richer fields in Part B |
| Out of scope (TASK-006) | Downloaders, TqSdk, real files, IV/Greeks implementation |
| Re-review gate | TASK-010 validates against first real MO samples |
| Breaking changes | Bump `schema_version`; update this document via Control Lane Issue |

See: [data_store_design.md](data_store_design.md), [data_migration_plan.md](data_migration_plan.md).
