# Data Migration Plan

**From:** `Option_System_Research` data platform  
**To:** `option_quant_fund` MVP data layer  
**Task:** TASK-005 — assessment and design only

---

## Overview

Current project (`option_quant_fund`) runs on **simulated sample CSV** (TASK-002). Legacy project has **production-oriented MO minute quote infrastructure** that must be **trimmed and re-implemented** under new module boundaries — not bulk-copied.

This plan defines staged migration from sample data → real MO minute order-book data.

---

## Stage 0 — Current sample schema (Done)

| Item | Detail |
|------|--------|
| **Goal** | Minimal CSV schema + loaders + option chain |
| **Input** | `data/sample/*.csv` |
| **Output** | Typed DataFrames, `build_option_chain()` |
| **Code** | TASK-001 ~ TASK-004 |
| **Real data** | No |
| **Risk** | Low — fixture only |

---

## Stage 1 — Adopt data_store layout & contracts (TASK-006)

| Item | Detail |
|------|--------|
| **Goal** | Formalize directory layout and parquet field contracts in docs + package stubs |
| **Input** | Legacy `data_store/` design, this review |
| **Output** | `data_store/` skeleton, `configs/data_catalog.json` (optional), layout helpers |
| **Code** | Yes — storage layout module, no network |
| **Real data** | No |
| **Risk** | Schema mismatch if over-specified before real samples |

**Deliverables:** path helpers, column enums, `.gitignore` rules, README updates.

---

## Stage 2 — TqSdk source adapter skeleton (TASK-007)

| Item | Detail |
|------|--------|
| **Goal** | Define adapter interface; mock/offline tests only |
| **Input** | Legacy `option_platform/data/sources/tq*.py` as **reference** |
| **Output** | `sources/tq/` interface, env-var auth guard, no live calls in CI |
| **Code** | Yes — skeleton + fakes |
| **Real data** | Optional manual smoke test outside CI |
| **Risk** | API tier / network; keep out of unit tests |

**Must not:** store `TQ_USER` / `TQ_PASS` in repo.

---

## Stage 3 — Single-contract MO minute quote download MVP (TASK-008)

| Item | Detail |
|------|--------|
| **Goal** | Download one MO option contract for one trade day → parquet |
| **Input** | TqSdk ticks via `get_tick_data_series` (or approved API) |
| **Output** | `data_store/quotes/minute/MO/{symbol}/{trade_date}.parquet` |
| **Code** | Yes — minimal downloader + align-to-minute |
| **Real data** | Yes — small scope |
| **Risk** | Account permissions, rate limits, stale quotes |

**Reuse from legacy:** atomic write, state JSON, `target_time` alignment, quality tags.

---

## Stage 4 — First real MO minute sample batch (TASK-009)

| Item | Detail |
|------|--------|
| **Goal** | Multi-day, multi-contract sample window (e.g. 5 trading days, four-term subset) |
| **Input** | Stage 3 downloader + skip-complete |
| **Output** | Local parquet corpus + quality summary JSON |
| **Code** | Yes — batch CLI, quality report |
| **Real data** | Yes — still local only |
| **Risk** | Volume, incomplete OTM quotes (expected — tag, don't hide) |

---

## Stage 5 — Four-term option chain snapshots (Post TASK-009)

| Item | Detail |
|------|--------|
| **Goal** | `data_store/snapshots/four_term/MO/{trade_date}.parquet` |
| **Input** | Minute quotes for expected four-term universe |
| **Output** | Daily chain snapshot parquet |
| **Code** | Yes — snapshot builder (new `src/` module) |
| **Real data** | Yes |
| **Risk** | Incomplete minute files → incomplete snapshot (by design) |

**Defer until:** TASK-009 quality gate acceptable on sample window.

---

## Stage 6 — Greeks / IV / Backtest (After TASK-010)

| Item | Detail |
|------|--------|
| **Goal** | IV/Greeks on validated snapshots |
| **Input** | Real snapshots + mark price rules |
| **Output** | Greeks module, backtest inputs |
| **Code** | Yes — separate Issues |
| **Real data** | Yes |
| **Risk** | Bad mark price → bad IV; enforce quality filters |

**Gate:** TASK-010 schema/chain re-review must pass before formal Greeks work.

---

## Migration Principles

1. **Design before download** — TASK-005/006 before TASK-008.
2. **Small batches** — one contract/day before full month.
3. **Quality over completeness** — tag missing OTM quotes; do not silently interpolate.
4. **No secrets in git** — credentials via environment only.
5. **No legacy strategy code** — data platform only.

---

## Suggested Issue Map

| Issue | Stage |
|-------|-------|
| TASK-005 (this) | Assessment + docs |
| TASK-006 | data_store layout & contracts |
| TASK-007 | TqSdk adapter skeleton |
| TASK-008 | Single-contract downloader MVP |
| TASK-009 | First real sample batch |
| TASK-010 | Schema + option_chain re-review on real data |
