# Data Directory Guide

**TASK-006** — formal layering for `data/` vs `data_store/`.

---

## Layout

```text
data/                              # Lightweight / staging
  sample/       # Simulated CSV fixtures — committed to git
  raw/          # Manual vendor drops — NOT committed
  processed/    # Normalized research exports — NOT committed
  external/     # Reference tables — NOT committed

data_store/     # Real MO historical parquet — NOT committed (repo root)
```

Full `data_store/` tree: [docs/data_store_design.md](../docs/data_store_design.md)

---

## Layer Purposes

| Layer | Path | Purpose | In GitHub? |
|-------|------|---------|------------|
| **sample** | `data/sample/` | TASK-002 CSV for tests/CI | Yes |
| **raw** | `data/raw/` | Temporary vendor exports before normalization | No |
| **processed** | `data/processed/` | Light transformed tables for ad-hoc research | No |
| **external** | `data/external/` | Calendars, mappings, third-party reference | No* |
| **data_store** | `data_store/` | Authoritative MO parquet corpus (minutes, ticks, snapshots) | **No** |

\*Exception: tiny, non-restricted reference files only — default is do not commit.

---

## `data/sample/`

- Files: `option_quotes_sample.csv`, `underlying_quotes_sample.csv`
- **Simulated data only** — not production MO schema
- Safe for CI; keep files small

---

## `data/raw/`

- One-off imports, vendor CSV/parquet drops, manual downloads
- **Staging only** — promote to `data_store/` layout after validation
- Never commit contents

---

## `data/processed/`

- Intermediate outputs (aggregates, joins, exports)
- Gitignored; not a substitute for `data_store/`

---

## `data/external/`

- Holiday calendars, manual symbol maps, third-party reference
- Gitignored by default

---

## `data_store/` (repository root)

Real historical MO data per [data_store_design.md](../docs/data_store_design.md):

```text
data_store/
  contracts/MO/{trade_date}.parquet
  ticks/MO/{symbol}/{trade_date}.parquet
  quotes/minute/MO/{symbol}/{trade_date}.parquet
  snapshots/four_term/MO/{trade_date}.parquet
  quality/MO/{symbol}/{trade_date}.state.json
```

- Format: **parquet** (data) + **JSON** (quality state)
- Field contracts: [data_dictionary.md](../docs/data_dictionary.md)
- **TASK-006:** structure documented only — no real files, no downloader

---

## Parquet vs CSV

| Format | Where | Committed? |
|--------|-------|------------|
| CSV | `data/sample/` only | Yes (fixtures) |
| CSV | anywhere else with real MO data | **Never** |
| Parquet | `data_store/**` | Local only — **never commit** |

---

## Security & Compliance

1. **Never commit** passwords, tokens, API keys, or `.env` files.
2. **Never commit** licensed or restricted real market data.
3. **Never commit** large parquet/CSV corpora.
4. Future TqSdk credentials: **`TQ_USER` / `TQ_PASS` environment variables only**.

---

## Related Docs

- [data_dictionary.md](../docs/data_dictionary.md) — Parts A–F field contracts
- [data_migration_plan.md](../docs/data_migration_plan.md) — staged migration
- [tqsdk_data_source_plan.md](../docs/tqsdk_data_source_plan.md) — TqSdk plan (TASK-007+)
