# Roadmap

## Current Phase: MVP 0.1

**Active task:** TASK-004 — Minimal option chain builder (Control Lane).

## Planned (high level)

| Task | Focus |
|------|--------|
| TASK-001 | Project skeleton, package layout, minimal tests |
| TASK-002 | Data dictionary and sample data conventions |
| TASK-003 | Fast Lane option chain prototype (experiments/) |
| TASK-004 | Formal option chain builder (`option_chain` module) |
| Later | Black-Scholes Greeks, backtest engine, risk rules |

## Principles

- Research and backtest first; no live trading in MVP
- Control Lane changes via GitHub Issue → Cursor → Review
- Fast Lane experiments stay under `experiments/` and `notebooks/`
