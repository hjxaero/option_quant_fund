# Data Directory Guide

## Layout

```text
data/
  sample/       # Small simulated CSV fixtures (committed)
  raw/          # Manual / semi-automated raw imports (not committed)
  processed/    # Normalized lightweight outputs (not committed)
  external/     # External reference data (not committed)

data_store/     # Real historical parquet (NOT in git — see repo root)
```

---

## `data/sample/`

- **Purpose:** MVP test fixtures and demos (TASK-002)
- **Files:** `option_quotes_sample.csv`, `underlying_quotes_sample.csv`
- **Committed:** Yes — safe simulated data only
- **Not** the final production MO minute schema

---

## `data/raw/`

- Dropped vendor exports, one-off files before normalization
- **Not committed** by default

---

## `data/processed/`

- Standardized intermediate tables for research
- **Not committed** by default

---

## `data/external/`

- Reference tables (calendars, mappings) from outside the project
- **Not committed** unless explicitly small and unrestricted

---

## `data_store/` (repository root)

- **Purpose:** Real MO historical data (minute quotes, ticks, snapshots)
- **Format:** Parquet + quality JSON state files
- **Default:** **Do not commit to GitHub**
- See [docs/data_store_design.md](../docs/data_store_design.md)

---

## Security & Compliance

1. **Never commit** account names, passwords, tokens, or API secrets.
2. **Never commit** licensed or restricted real market data.
3. **Never commit** large parquet corpora — keep them local.
4. Credentials for TqSdk (future) use **`TQ_USER` / `TQ_PASS` environment variables only**.

---

## Related Docs

- [data_dictionary.md](../docs/data_dictionary.md) — field schemas
- [data_migration_plan.md](../docs/data_migration_plan.md) — staged migration from sample → real data
- [tqsdk_data_source_plan.md](../docs/tqsdk_data_source_plan.md) — TqSdk integration plan (no code in TASK-005)
