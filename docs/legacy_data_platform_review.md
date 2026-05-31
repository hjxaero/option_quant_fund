# Legacy Data Platform Review

**Source repository:** [Option_System_Research](https://github.com/hjxaero/Option_System_Research)  
**Review task:** TASK-005 (Control Lane)  
**Scope:** Migration assessment and design only — **no code copied in this task**

---

## 1. Legacy Project Positioning

`Option_System_Research` is a MO (CSI 1000 index options) **data platform** project. Its current mainline is building a reusable, auditable market-data middle layer — not live trading, not strategy execution.

Core focus in the legacy repo:

| Dimension | Legacy choice |
|-----------|---------------|
| Data source | Tianqin **TqSdk** |
| First product | **MO** (CFFEX CSI 1000 index options) |
| Primary granularity | **1-minute order-book aligned quotes** |
| Contract universe | **Four-term pool** (current month, next month, current quarter, next quarter) |
| Storage root | `data_store/` (parquet, default not in git) |
| Downstream | IV surface, Greeks, snapshots — designed but partially implemented |

The legacy platform already validates: tick download → minute alignment → parquet upsert → quality state files → four-term snapshots.

---

## 2. Legacy Data Platform Module Overview

```text
option_platform/data/
  sources/          # TqSdk adapters (ticks, minute quotes, contracts)
  storage/          # layout, state, atomic upsert
  quality/          # quote quality, gate, repair plans
  snapshots/        # four-term snapshot builders
  contracts.py      # contract metadata contracts
  universe.py       # four-term selection
  trading_minutes.py
  pricing.py        # mark price from order book
  iv_surface.py     # IV surface (downstream)

scripts/            # CLI entry points (download, update, snapshot build)
docs/               # data_platform, project_rules, iv_surface_pipeline
data_store/         # parquet assets (local only)
```

Key operational patterns documented in legacy `docs/data_platform.md` and `docs/project_rules.md`:

- **Checkpoint resume:** skip complete minute files; snapshot layer skips complete days
- **Atomic writes:** temp parquet → rename
- **Quality tags:** `quote_quality`, `quote_age_ms`, `spread_bps`, state JSON per symbol/day
- **Order book first:** IV/Greeks prefer bid/ask micro/mid over last price
- **Credentials:** `TQ_USER` / `TQ_PASS` from environment only

---

## 3. Migration Classification

### A. 立即吸收 (Adopt now — design principles)

| Asset | Rationale |
|-------|-----------|
| Data platform positioning | Single source of truth for market data; strategies read from platform |
| `data_store/` layout concept | contracts / ticks / minute quotes / snapshots / quality |
| `data_store/` default not in git | Large licensed data must stay local |
| Env-var credentials (`TQ_USER`, `TQ_PASS`) | No secrets in repo |
| Four-term contract pool | Standard MO snapshot universe |
| Quality tags | Trace bad quotes instead of silent fill |
| Checkpoint resume | Idempotent batch downloads |
| Atomic parquet writes | Avoid half-written files |
| Order book over last price | Pricing input priority for future IV |
| Scripts as CLI only, logic in package | Matches current `src/` boundary |
| Minute trading calendar (09:30–11:30, 13:00–15:00) | MO alignment baseline |
| `target_time` / `quote_time` / `quote_age_ms` | Auditability of aligned quotes |

### B. 后续迁移 (Migrate in later tasks)

| Asset | Suggested task |
|-------|----------------|
| Storage layout module | TASK-006 |
| Contract metadata schema | TASK-006 |
| TqSdk source adapter skeleton | TASK-007 |
| Minute quote downloader MVP | TASK-008 |
| State files + skip-complete logic | TASK-008 |
| Quality gate / report scripts | TASK-009 |
| Four-term snapshot builder | After TASK-009 |
| `first_valid_dates.json` cache | TASK-008+ |
| Live incremental update window | Post-MVP |

### C. 暂缓迁移 (Defer)

| Asset | Reason |
|-------|--------|
| IV surface pipeline | Needs real minute samples + schema lock (post TASK-010) |
| Greeks / Black-76 / BS IV solver | Depends on mark price + T |
| Margin / seller margin fields | Strategy layer, not data MVP |
| SVI / SABR / SSVI smoothing | Explicitly out of legacy v0 scope |
| `live_update.py` intraday production loop | After downloader stable |
| Benchmark / probe scripts | Port when testing infra ready |
| Legacy `DualSellRunner` / factor backtest | Different project goal |

### D. 不迁移 (Do not migrate)

| Asset | Reason |
|-------|--------|
| Old strategy scripts (`archive/`, dual-sell factors) | Bound to legacy research, not data platform |
| Hard-coded Windows paths (`E:\Option_Sell_Research`) | Environment-specific |
| Any credentials in docs/examples beyond env-var pattern | Security |
| 1-minute K-line as pseudo order book | Explicitly forbidden in legacy rules |
| Direct copy of `legacy_tq_mo` compatibility shim | Re-implement under new package boundaries |
| Live trading / broker / OMS logic | Out of project scope |

---

## 4. Risk Points

| Risk | Mitigation |
|------|------------|
| TqSdk network / account tier limits | Probe scripts before bulk download; no downloader in TASK-005 |
| `get_tick_data_series` requires pro API | Document in tqsdk plan; fallback scope limited |
| Deep OTM / far-month missing quotes | Quality tags + known liquidity limits, not download failure |
| Large parquet volume | `data_store/` gitignored; monthly chunking |
| Schema drift between legacy and new project | TASK-010 re-review after first real samples |
| Premature IV/Greeks | Roadmap blocks formal Greeks until TASK-009/010 |

---

## 5. CTO Migration Recommendations

1. **Do not copy legacy Python into `option_quant_fund` in one step.** Absorb directory layout and contracts first (TASK-006).
2. **Keep TASK-002 sample CSV** as the lightweight test fixture; real MO data lives in `data_store/` parquet.
3. **Implement TqSdk adapter in a dedicated Issue** (TASK-007+) with env-var auth only.
4. **First real data milestone:** single-contract MO minute quote parquet for one trade day (TASK-008/009).
5. **Re-validate option chain builder** against real samples (TASK-010) before Greeks module work.
6. **Treat IV surface docs as reference only** until minute quote quality gate passes on a full sample window.

---

## 6. Explicit Non-Goals (TASK-005)

- No legacy code copied into this repository in this task
- No TqSdk connection or downloader implementation
- No real market data download
- No account passwords, tokens, or secrets in any file
