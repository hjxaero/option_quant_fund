# Data Dictionary

> **MVP 0.1 minimal schema** — simulated sample data only.  
> This is **not** the final production exchange format.

All timestamps use ISO-like strings in CSV (`YYYY-MM-DD HH:MM:SS`) and are parsed to `datetime64` on load.  
No real account data, API keys, or live market feeds are included.

---

## Option Quote Schema

File example: `data/sample/option_quotes_sample.csv`

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

### Data quality rules (MVP 0.1)

- `option_type` must be exactly `C` or `P`.
- `bid_price` must be less than `ask_price`.
- `strike`, prices, and `underlying_price` must be numeric.
- `volume` and `open_interest` must be integers ≥ 0 in sample data.
- Missing required columns cause `ValueError` in the loader.

---

## Underlying Quote Schema

File example: `data/sample/underlying_quotes_sample.csv`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `timestamp` | datetime | Yes | Quote time, e.g. `2025-01-02 09:31:00` |
| `underlying_symbol` | string | Yes | Underlying ticker, e.g. `IM` |
| `last_price` | float | Yes | Last traded price |
| `bid_price` | float | Yes | Best bid |
| `ask_price` | float | Yes | Best ask |
| `volume` | int | Yes | Session volume |

### Data quality rules (MVP 0.1)

- `bid_price` must be less than `ask_price`.
- Price fields must be numeric; `volume` must be integer.
- Missing required columns cause `ValueError` in the loader.

---

## Loader API

| Function | Input | Output |
|----------|-------|--------|
| `load_option_quotes(path)` | Option quote CSV path | `pandas.DataFrame` with typed columns |
| `load_underlying_quotes(path)` | Underlying quote CSV path | `pandas.DataFrame` with typed columns |

Loaders perform column presence checks and basic type coercion only. They do **not** compute Greeks, build option chains, or run backtests.

---

## Out of scope (TASK-002)

- Live exchange feeds, tick/Level-2 data, databases
- Data cleaning pipelines beyond type coercion
- Production-grade field coverage

Future tasks may extend this dictionary for processed datasets and chain-ready views.
