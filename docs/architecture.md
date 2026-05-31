# Architecture

## Overview

`option_quant_fund` is an option quant **research platform MVP** (version 0.1). It is **not** a live trading system.

## Control Lane vs Fast Lane

| Lane | Location | Purpose |
|------|----------|---------|
| **Control Lane** | `src/option_quant_fund/`, `tests/`, `docs/`, `configs/` | Formal, reviewable production skeleton |
| **Fast Lane** | `experiments/`, `notebooks/` | Disposable prototypes and research; must not become core production code |

## Module Boundaries

### `data`

- Data loading and normalization interface placeholders
- Sample data read placeholders

Does **not** handle: Greeks, strategy signals, backtest, live trading.

### `option_chain`

- Option chain construction interface placeholders
- Expiry, strike, Call/Put structure placeholders

Does **not** handle: Greeks, trading signals, backtest, execution.

### `greeks`

- Greeks calculation interface placeholders
- Black-Scholes implementation deferred to TASK-004

Does **not** handle: risk limits, auto-hedging, trading decisions.

### `backtest`

- Backtest workflow interface placeholders
- Future integration with data, option_chain, greeks

Does **not** handle: real matching, complex slippage, live simulation.

### `risk`

- Minimal risk limit interface placeholders
- Future: max_delta, max_gamma, max_loss rules

Does **not** handle: Portfolio Risk Brain, real-time risk, OMS/EMS.

## Out of Scope (TASK-001)

- Live trading, broker APIs, auto order placement
- OMS / EMS, Portfolio Risk Brain
- Multi-agent orchestration, GitHub Workflow Agent
