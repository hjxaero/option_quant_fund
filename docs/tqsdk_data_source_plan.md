# TqSdk Data Source Plan

**Task:** TASK-005 — planning document only  
**Status:** No TqSdk connection code in this repository as part of TASK-005

---

## 1. Role of TqSdk in Legacy Project

In `Option_System_Research`, Tianqin **TqSdk** is the primary external market data source for MO options:

| Capability | Legacy usage |
|------------|--------------|
| Contract discovery | `query_quotes(expired=True)` for historical MO |
| Tick history | `get_tick_data_series()` — pro API, network-bound |
| Live quotes | `get_quote()` + `wait_update()` |
| Batch download | Scripts wrapping tick → minute alignment |

Legacy modules (reference only): `option_platform/data/sources/tq.py`, `tq_ticks.py`, `tq_minute_quotes.py`, `tq_contracts.py`.

---

## 2. Should `option_quant_fund` Connect to TqSdk Now?

**No — not in TASK-005.**

| Phase | TqSdk action |
|-------|--------------|
| TASK-005 (now) | Document plan only |
| TASK-007 | Adapter **skeleton** + offline tests |
| TASK-008 | First **manual** download MVP (single contract/day) |
| TASK-009+ | Batch downloads with checkpoint resume |

Rationale: schema and storage layout must be fixed before live API coupling.

---

## 3. Credential Policy

| Rule | Detail |
|------|--------|
| Environment variables | `TQ_USER`, `TQ_PASS` only |
| Forbidden in repo | Passwords, tokens, API keys, `.env` with secrets |
| Forbidden in docs | Real account values (use placeholders) |
| CI | No live TqSdk calls in default `pytest` |

Example (local manual run only):

```bash
export TQ_USER="your_username"
export TQ_PASS="your_password"
# Run downloader in TASK-008+ — not available in TASK-005
```

---

## 4. What TASK-005 Does NOT Do

- **No** TqSdk import or `TqApi` instantiation in this task
- **No** downloader scripts
- **No** real network calls to Tianqin
- **No** credential storage

Implementation belongs to **separate Issues** (TASK-007, TASK-008).

---

## 5. Planned Adapter Boundary (Future)

```text
src/option_quant_fund/data/sources/tq/   # future TASK-007+
  client.py       # env-var auth, context manager, explicit close
  contracts.py    # MO universe / four-term selection
  ticks.py        # tick download (optional layer)
  minute_quotes.py
```

Scripts remain thin CLI wrappers; business logic stays in `src/`.

---

## 6. Risks & Constraints

| Risk | Impact | Mitigation |
|------|--------|------------|
| Network latency | Slow bulk history | Monthly chunks; 4–6 workers (legacy benchmark) |
| Account tier | `get_tick_data_series` may be unavailable | Probe script before bulk; document fallback limits |
| Connection limits | Too many parallel `TqApi` | Cap workers; no overlapping batch jobs |
| Stale / missing OTM quotes | High `missing_ratio` on deep strikes | Quality tags; not a download failure |
| Windows vs macOS paths | Legacy scripts use PowerShell | Re-implement paths via `pathlib` in new project |
| K-line misuse | 1-min OHLC lacks order book | **Never** use K-line as IV input (legacy rule) |

---

## 7. First Minimal Download Capability (Phase 1 Target)

When implementation begins (TASK-008), prioritize:

1. **One MO option symbol**
2. **One trade date**
3. Tick → standard minute axis alignment
4. Output: `data_store/quotes/minute/MO/{symbol}/{trade_date}.parquet`
5. Sidecar: `data_store/quality/MO/{symbol}/{trade_date}.state.json`
6. Atomic write (temp file → rename)

Defer four-term batch, snapshot build, and IV until TASK-009/010.

---

## 8. Explicit Statement

> **TASK-005 不实现任何 TqSdk 连接代码。**

This document is the approved plan; code comes in later Control Lane Issues with separate review.
