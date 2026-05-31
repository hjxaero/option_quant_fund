# Roadmap

## Current Phase: MVP 0.1 — Data Platform Migration

**Active task:** TASK-007 — TqSdk source adapter skeleton (Control Lane).

**Completed:**

| Task | Focus |
|------|--------|
| TASK-001 | Project skeleton |
| TASK-002 | Sample schema / data loader |
| TASK-003 | Option chain Fast Lane prototype |
| TASK-004 | Formal option chain builder |
| TASK-005 | Legacy platform review & migration plan docs |
| TASK-006 | `data_store` directory structure and data contracts |

---

## Data Migration Track

| Task | Focus | Real data? | Status |
|------|--------|------------|--------|
| TASK-005 | Legacy review; initial store design docs | No | Done |
| TASK-006 | Formal `data_store` layout + field contracts + `.gitignore` | No | Done |
| **TASK-007** | TqSdk source adapter skeleton (offline tests; env-var auth) | No | **Current** |
| **TASK-008** | Single-contract MO minute quote download MVP | Yes (minimal) | **Next** |
| TASK-009 | First real MO sample batch + quality report | Yes | Planned |
| TASK-010 | Re-review schema & option_chain on real samples | Yes | Planned |

### TASK-008 (next)

- First parquet under `data_store/quotes/minute/MO/{symbol}/{trade_date}.parquet`
- Atomic write + `.state.json` sidecar
- **No** four-term batch yet

---

## Greeks / Backtest Gate

**Do not start formal Greeks until TASK-009 and TASK-010 complete.**

| Future area | Depends on |
|-------------|------------|
| Black-Scholes / Black-76 Greeks | TASK-010 + snapshot quality |
| Backtest engine | Greeks + snapshots |
| Risk limits | Backtest + positions model |

---

## Principles

- Research and backtest first; **no live trading** in MVP
- Control Lane: GitHub Issue → Cursor → Review
- `data_store/` real data stays **local**, not in git
- Credentials via **environment variables only**

---

## Reference Docs

| Doc | Purpose |
|-----|---------|
| [legacy_data_platform_review.md](legacy_data_platform_review.md) | TASK-005 legacy assessment |
| [data_migration_plan.md](data_migration_plan.md) | Stage 0–6 migration plan |
| [data_store_design.md](data_store_design.md) | TASK-006 directory contract |
| [data_dictionary.md](data_dictionary.md) | Field-level contracts |
| [tqsdk_data_source_plan.md](tqsdk_data_source_plan.md) | TqSdk adapter plan |
