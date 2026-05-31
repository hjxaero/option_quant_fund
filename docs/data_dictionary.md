# Data Dictionary

> **MVP 0.1** — includes TASK-002 sample schemas **and** candidate fields for future real MO minute data.  
> Sample CSV is **not** the final production format. Real data will use parquet under `data_store/`.

No real account data, API keys, or live feeds are stored in this repository.

---

## Part A — MVP Sample Schemas (TASK-002, current)

### Option Quote CSV (sample)

File: `data/sample/option_quotes_sample.csv`

| Field | Type | Required now | Description |
|-------|------|--------------|-------------|
| `timestamp` | datetime | Yes | Quote time |
| `underlying_symbol` | string | Yes | Underlying ticker (sample: `IM`) |
| `option_symbol` | string | Yes | Option contract code |
| `expiry` | date | Yes | Expiration date |
| `strike` | float | Yes | Strike price |
| `option_type` | string | Yes | `C` or `P` |
| `bid_price` | float | Yes | Best bid |
| `ask_price` | float | Yes | Best ask |
| `last_price` | float | Yes | Last traded price |
| `volume` | int | Yes | Session volume |
| `open_interest` | int | Yes | Open interest |
| `underlying_price` | float | Yes | Underlying reference price |

### Underlying Quote CSV (sample)

File: `data/sample/underlying_quotes_sample.csv`

| Field | Type | Required now | Description |
|-------|------|--------------|-------------|
| `timestamp` | datetime | Yes | Quote time |
| `underlying_symbol` | string | Yes | Underlying ticker |
| `last_price` | float | Yes | Last traded price |
| `bid_price` | float | Yes | Best bid |
| `ask_price` | float | Yes | Best ask |
| `volume` | int | Yes | Session volume |

### Sample quality rules

- `option_type` ∈ {`C`, `P`}; `bid_price` < `ask_price`
- Missing columns → `ValueError` in loader

---

## Part B — MO Minute Quote Candidates (future, parquet)

Target path: `data_store/quotes/minute/MO/{symbol}/{trade_date}.parquet`  
Aligned from TqSdk ticks (see legacy `Option_System_Research` data platform).

| Field | Type | Required now | Required future | Description |
|-------|------|--------------|-----------------|-------------|
| `target_time` | datetime | No | Yes | Standard minute slot (MO session grid) |
| `quote_time` | datetime | No | Yes | Source tick timestamp used for alignment |
| `quote_age_ms` | int | No | Yes | `target_time - quote_time` in ms |
| `symbol` | string | No | Yes | Full contract code (e.g. `CFFEX.MO2601-C-6000`) |
| `underlying_symbol` | string | No | Yes | Underlying / index reference |
| `expiry_date` | date | No | Yes | Contract expiration |
| `strike_price` | float | No | Yes | Strike |
| `option_type` | string | No | Yes | `call` / `put` or `C` / `P` (normalize in TASK-006) |
| `bid_price1` | float | No | Yes | Best bid (level 1) |
| `ask_price1` | float | No | Yes | Best ask (level 1) |
| `bid_volume1` | int | No | Yes | Bid size |
| `ask_volume1` | int | No | Yes | Ask size |
| `last_price` | float | No | Optional | Last trade — not primary IV input |
| `volume` | int | No | Optional | Session volume |
| `open_interest` | int | No | Optional | Open interest |
| `mid_price` | float | No | Yes | (bid + ask) / 2 when valid |
| `micro_price` | float | No | Yes | Volume-weighted micro price |
| `spread_bps` | float | No | Yes | Bid-ask spread in bps |
| `price_source` | string | No | Yes | `micro`, `mid`, `last_inside_spread`, `last`, `none` |
| `quote_quality` | string | No | Yes | e.g. `ok`, `stale_quote`, `wide_spread`, `no_price` |

**Design rule (from legacy):** prefer order book over last price for future mark/IV inputs.

---

## Part C — Contract Metadata Candidates (future)

Target path: `data_store/contracts/MO/{trade_date}.parquet`

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

Supporting cache (future): `data_store/contracts/MO/first_valid_dates.json` — first day with usable quotes per symbol.

---

## Part D — Four-Term Snapshot Candidates (future)

Target path: `data_store/snapshots/four_term/MO/{trade_date}.parquet`

Extends minute quote fields with chain context:

| Field | Type | Required now | Required future | Description |
|-------|------|--------------|-----------------|-------------|
| `timestamp` | datetime | No | Yes | Standard minute (alias of `target_time`) |
| `term_role` | string | No | Yes | Four-term role |
| `futures_symbol` | string | No | Optional | Pricing forward instrument |
| `futures_price` | float | No | Optional | Forward/futures input for IV |
| `mark_price` | float | No | Future | Price used for IV/Greeks |
| `iv` | float | No | Deferred | Implied vol — **not in TASK-005~010 data tasks** |
| `iv_quality` | string | No | Deferred | IV quality tag |
| `iv_method` | string | No | Deferred | `calc`, `interp`, `none` |

Snapshot rows inherit bid/ask/micro/mid/quality fields from Part B.

---

## Loader API (current)

| Function | Input | Output |
|----------|-------|--------|
| `load_option_quotes(path)` | Sample CSV path | DataFrame (Part A columns) |
| `load_underlying_quotes(path)` | Sample CSV path | DataFrame (Part A columns) |

Future loaders for parquet (TASK-006+) will be documented here when implemented.

---

## Schema Evolution Notes

| Topic | Decision |
|-------|----------|
| Sample vs production | Sample CSV stays for CI; production uses parquet |
| Greeks / IV fields | Documented as future; **not implemented** in data migration Phase 1 |
| Field naming | Production parquet uses snake_case English (legacy convention) |
| Re-review gate | TASK-010 validates schema against first real MO samples |

See also: [data_store_design.md](data_store_design.md), [data_migration_plan.md](data_migration_plan.md).
