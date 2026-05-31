# Roadmap

## Current Phase: MVP 0.1 — Data Platform Migration

**Active task:** TASK-005 — Legacy data platform review and migration plan (Control Lane).

**Completed:**

| Task | Focus |
|------|--------|
| TASK-001 | Project skeleton |
| TASK-002 | Sample schema / data loader |
| TASK-003 | Option chain Fast Lane prototype |
| TASK-004 | Formal option chain builder |

---

## Data Migration Track (TASK-005+)

| Task | Focus | Real data? |
|------|--------|------------|
| **TASK-005** | Review legacy platform; migration & store design docs | No |
| **TASK-006** | `data_store` layout, data contracts, `.gitignore` | No |
| **TASK-007** | TqSdk source adapter skeleton (no CI network) | No |
| **TASK-008** | Single-contract MO minute quote download MVP | Yes (minimal) |
| **TASK-009** | First real MO minute sample batch + quality report | Yes |
| **TASK-010** | Re-review schema & option_chain on real samples | Yes |

---

## Greeks / Backtest Gate

**Do not start formal Greeks module until TASK-009 and TASK-010 complete.**

Rationale (from legacy review):

- IV/Greeks require validated minute order-book quotes and mark price rules
- Sample CSV alone is insufficient for production IV
- Option chain must be re-validated on real MO parquet before Greeks

Planned after data track:

| Future area | Depends on |
|-------------|------------|
| Black-Scholes / Black-76 Greeks | TASK-010 + snapshot quality |
| Backtest engine | Greeks + snapshots |
| Risk limits | Backtest + positions model |

---

## Principles

- Research and backtest first; **no live trading** in MVP
- Control Lane: GitHub Issue → Cursor → Review
- Fast Lane: `experiments/`, `notebooks/` — disposable prototypes
- `data_store/` real data stays **local**, not in git
- Credentials via **environment variables only** (`TQ_USER`, `TQ_PASS`)

---

## Legacy Reference

Source: [Option_System_Research](https://github.com/hjxaero/Option_System_Research)

- Review: [legacy_data_platform_review.md](legacy_data_platform_review.md)
- Plan: [data_migration_plan.md](data_migration_plan.md)
