# Data Store Design

**Version:** MVP 0.1 (TASK-005 design)  
**Status:** Specification only — no downloader in this task

---

## Purpose

Define where **real historical market data** lives in `option_quant_fund`, separate from small **sample fixtures** under `data/`.

Inspired by legacy `Option_System_Research/data_store/` layout, trimmed for current project boundaries.

---

## Directory Layout

```text
data/
  sample/           # Small CSV fixtures (committed, for tests/demos)
  raw/              # Manual or semi-automated raw imports (usually not committed)
  processed/        # Lightweight normalized exports (usually not committed)
  external/         # External reference files (usually not committed)

data_store/         # Real historical parquet assets (default NOT in git)
  contracts/{product}/{trade_date}.parquet
  ticks/{product}/{symbol}/{trade_date}.parquet
  quotes/minute/{product}/{symbol}/{trade_date}.parquet
  snapshots/four_term/{product}/{trade_date}.parquet
  quality/{product}/{symbol}/{trade_date}.state.json
```

**First product:** `MO` (CFFEX CSI 1000 index options)  
**Primary format:** **parquet** (snake_case English column names)

---

## `data/` vs `data_store/`

| Aspect | `data/` | `data_store/` |
|--------|---------|---------------|
| Purpose | Fixtures, staging, light processed files | Production-scale historical assets |
| Typical size | KB – low MB | GB+ |
| Default in git | `sample/` yes; others usually no | **No** |
| Format | CSV (sample), ad hoc | Parquet |
| Used by tests | Yes (`sample/`) | Optional local integration only |
| License / auth | Public simulated data only | Licensed market data — local only |

---

## Layer Descriptions

### `data/sample/`

- TASK-002 CSV schemas (`option_quotes_sample.csv`, `underlying_quotes_sample.csv`)
- **Committed** — enables CI without real data
- **Not** a substitute for production MO minute schema

### `data/raw/`

- Dropped exports, vendor files, one-off downloads before normalization
- Gitignored by default

### `data/processed/`

- Intermediate normalized tables (e.g. daily aggregates for research)
- Gitignored by default

### `data/external/`

- Reference tables (holiday calendars, manual mappings)
- Gitignored unless explicitly small and non-restricted

### `data_store/contracts/`

- Daily contract universe / metadata snapshots
- Fields (future): symbol, expiry, strike, option_type, term_role, multiplier, tick_size

### `data_store/ticks/`

- Raw tick parquet per symbol per trade day (optional layer; may skip if minute-only MVP)

### `data_store/quotes/minute/`

- **Stage 1 real-data target:** 1-minute order-book-aligned quotes
- One file per `{product}/{symbol}/{trade_date}.parquet`
- Core fields: `target_time`, `quote_time`, `quote_age_ms`, bid/ask, volumes, quality tags

### `data_store/snapshots/four_term/`

- Daily four-term option chain snapshot (all expected contracts × minutes)
- Built only when underlying minute files pass completeness checks

### `data_store/quality/`

- Per-symbol per-day `.state.json` (rows, last_target_time, updated_at)
- Summary JSON for batch quality reports

---

## Git Policy

1. **`data_store/` must not be committed** — add to `.gitignore`.
2. **Do not commit** licensed or restricted real market data.
3. **Do not commit** account credentials, API keys, tokens, or secrets.
4. **`data/sample/`** remains the only routine data committed to GitHub.
5. Large parquet belongs on local disk or approved external storage — not the repo.

---

## Implementation Notes (Future Tasks)

| Task | Action |
|------|--------|
| TASK-006 | Create layout helpers + catalog; add `.gitignore` entries |
| TASK-008 | Write first minute quote parquet |
| TASK-009 | Batch download + quality summaries |
| TASK-010 | Align loaders with real schema |

**TASK-005 does not create downloader code or real parquet files.**
