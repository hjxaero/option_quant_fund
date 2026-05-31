# Data Store Design

**Version:** MVP 0.1 — TASK-006 (formal contract)  
**Status:** Directory layout and field contracts defined; **no downloader, no real data files**

---

## Purpose

Formalize where **real MO (CSI 1000 index options) historical data** lives, separate from lightweight fixtures under `data/`.

Migrated from legacy `Option_System_Research/data_store/` design (TASK-005 review), trimmed for `option_quant_fund` boundaries.

**This document is the source of truth for TASK-006.** Implementation code (path helpers, loaders) arrives in TASK-007+.

---

## Top-Level Layout

```text
data/                              # Lightweight / staging (see data/README.md)
  sample/                          # Simulated CSV — committed
  raw/                             # Manual imports — not committed
  processed/                       # Normalized exports — not committed
  external/                        # Reference tables — not committed

data_store/                        # Real historical assets — NOT committed
  contracts/{product}/
    {trade_date}.parquet
    first_valid_dates.json         # per-product cache (optional)
  ticks/{product}/{symbol}/
    {trade_date}.parquet
  quotes/minute/{product}/{symbol}/
    {trade_date}.parquet
  snapshots/four_term/{product}/
    {trade_date}.parquet
  quality/{product}/{symbol}/
    {trade_date}.state.json
  quality/{product}/               # batch summaries (optional)
    {batch_id}_summary.json
```

**First product:** `MO` (CFFEX CSI 1000 index options)  
**Primary format:** **Parquet** (snake_case English columns)  
**Quality sidecars:** **JSON** (`.state.json`, summary reports)

---

## `data/` vs `data_store/`

| Aspect | `data/` | `data_store/` |
|--------|---------|---------------|
| Purpose | Fixtures, staging, light research exports | Authoritative local historical corpus |
| Typical size | KB – low MB | GB+ |
| In git | `sample/` only (by default) | **Never** (except `.gitkeep`) |
| Formats | CSV (sample), ad hoc | Parquet + JSON state |
| Used in CI | Yes (`sample/`) | No |
| License | Simulated / public fixtures | Licensed market data — local only |
| Downloader output | Should not land here long-term | **Yes** — primary sink |

---

## Layer Descriptions (`data/`)

| Layer | Path | Role | Committed? |
|-------|------|------|------------|
| **sample** | `data/sample/` | TASK-002 CSV fixtures for tests/demos | Yes |
| **raw** | `data/raw/` | Dropped vendor exports before normalization | No |
| **processed** | `data/processed/` | Intermediate normalized tables | No |
| **external** | `data/external/` | Calendars, mappings, reference CSV | No (unless tiny + unrestricted) |

**Rule:** Downloader output must **not** stay in `data/raw/` permanently — promote to `data_store/` parquet layout.

---

## Layer Descriptions (`data_store/`)

### `contracts/{product}/{trade_date}.parquet`

Daily contract universe for product `MO` on trade date.

- One row per listed option contract expected that day
- Includes `term_role` for four-term pool members
- See [data_dictionary.md — Part C](data_dictionary.md)

### `ticks/{product}/{symbol}/{trade_date}.parquet`

Raw tick stream (optional layer; may defer if minute-only MVP in TASK-008).

- `{symbol}` = exchange-qualified code, e.g. `CFFEX.MO2601-C-6000`
- `{trade_date}` = `YYYY-MM-DD` (session date)
- See [data_dictionary.md — Part E](data_dictionary.md)

### `quotes/minute/{product}/{symbol}/{trade_date}.parquet`

**Primary real-data target (TASK-008+).** One-minute order-book-aligned quotes.

- MO session grid: `09:30–11:30`, `13:00–15:00` (240 minutes)
- Alignment: nearest tick with `quote_time <= target_time`
- See [data_dictionary.md — Part B](data_dictionary.md)

### `snapshots/four_term/{product}/{trade_date}.parquet`

Daily four-term option chain snapshot (all expected contracts × minutes).

- Built only when minute quote completeness checks pass
- See [data_dictionary.md — Part D](data_dictionary.md)

### `quality/{product}/{symbol}/{trade_date}.state.json`

Per-file download/update state (rows, timestamps, checksum hints).

- See [data_dictionary.md — Part F](data_dictionary.md)

---

## File Naming Conventions

| Token | Format | Example |
|-------|--------|---------|
| `{product}` | Uppercase product code | `MO` |
| `{symbol}` | Exchange-qualified contract | `CFFEX.MO2601-C-6000` |
| `{trade_date}` | ISO date | `2026-01-17` |
| `{batch_id}` | `{product}_{start}_{end}` | `MO_20260112_20260116` |

**Rules:**

1. Use `/` path separators; no Windows drive paths in docs or code.
2. `{trade_date}` is the **trading session date**, not file creation time.
3. Parquet files are **immutable per (symbol, trade_date)** once marked complete; updates use atomic replace (see below).
4. Temp writes use `*.parquet.tmp` beside target — never commit temps.

---

## MO Four-Term Contract Pool

Standard term roles (legacy convention):

| `term_role` | Meaning |
|-------------|---------|
| `current_month` | Nearest monthly expiry |
| `next_month` | Second monthly expiry |
| `current_quarter` | Nearest quarterly expiry |
| `next_quarter` | Second quarterly expiry |

**Rules:**

1. Each snapshot row must carry `term_role` when part of four-term universe.
2. If monthly and quarterly expiries coincide, quarter roles **shift forward** to preserve four distinct expiries when market listing allows.
3. Contract selection logic belongs in the data platform (TASK-007+), not in strategy modules.

---

## Parquet vs CSV Rules

| Use case | Format | Location |
|----------|--------|----------|
| CI test fixtures | CSV | `data/sample/` only |
| Real minute quotes | Parquet | `data_store/quotes/minute/` |
| Real ticks | Parquet | `data_store/ticks/` |
| Contract metadata | Parquet | `data_store/contracts/` |
| Snapshots | Parquet | `data_store/snapshots/four_term/` |
| Download state | JSON | `data_store/quality/` |
| Ad hoc research export | CSV optional | `data/processed/` (local, gitignored) |

**Parquet constraints (TASK-006 contract):**

- Column names: `snake_case` English
- dtypes documented in [data_dictionary.md](data_dictionary.md)
- Optional `schema_version` column or file metadata field `v1` until breaking change
- No mixed-type columns; nullable fields explicit

**CSV constraints:**

- Sample CSV only in `data/sample/` for git
- Real MO exports must not be committed as CSV blobs

---

## Version & Schema Management

| Mechanism | Purpose |
|-----------|---------|
| `schema_version` in parquet metadata or first-class column | Breaking field changes |
| Git-tracked docs (`data_dictionary.md`) | Human-readable contract |
| TASK-010 gate | Re-validate loaders against real samples before Greeks |

**TASK-006 does not implement schema validation code** — documents the contract only.

---

## Write & Resume Principles (Design — TASK-008+)

From legacy platform; required for future downloaders:

1. **Atomic write:** write `*.parquet.tmp` → rename to final path
2. **Checkpoint resume:** skip files marked complete in `.state.json`
3. **Idempotent merge:** dedupe on `(symbol, target_time)` keeping best `quote_quality`
4. **No partial snapshots:** do not build four-term snapshot if minute files missing

---

## Git Policy

| Content | Commit to GitHub? |
|---------|-------------------|
| `data/sample/*.csv` | Yes (simulated, small) |
| `data/raw/`, `processed/`, `external/` contents | **No** |
| `data_store/**` parquet/json data | **No** |
| `data_store/.gitkeep` | Yes (empty placeholder) |
| `.env`, credentials, tokens | **Never** |
| Licensed / restricted real market data | **Never** |
| Large parquet / CSV corpora | **Never** |

---

## Task Map

| Task | Deliverable |
|------|-------------|
| TASK-005 | Migration assessment (done) |
| **TASK-006** | This document + field contracts (done) |
| TASK-007 | TqSdk adapter skeleton (no CI network) |
| TASK-008 | Single-contract minute quote download MVP |
| TASK-009 | Batch samples + quality reports |
| TASK-010 | Schema / option_chain re-review on real data |

**TASK-006:** no downloader, no TqSdk imports, no real parquet files created.
