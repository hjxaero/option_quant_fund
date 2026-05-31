# Option Chain Prototype (Fast Lane)

**Lane:** Fast Lane experiment — **not** a production module.

This directory validates whether TASK-002 option quote data can be grouped into a minimal option chain structure before any Control Lane implementation in `src/option_quant_fund/option_chain/chain_builder.py`.

## Purpose

1. Load `data/sample/option_quotes_sample.csv` via `load_option_quotes`
2. Group quotes by `expiry`
3. Sort by `strike` within each expiry
4. Separate Call (`C`) and Put (`P`) legs
5. Produce a nested dict and summary DataFrame for review

This experiment does **not** compute Greeks, IV, backtests, signals, or trading logic.

## Run

From the repository root:

```bash
PYTHONPATH=src python experiments/option_chain_prototype/prototype_option_chain.py
```

Optional tests:

```bash
PYTHONPATH=src python -m pytest tests/test_option_chain_prototype.py -v
```

## Next step (Control Lane)

If the structure looks good, promote the design into `src/option_quant_fund/option_chain/chain_builder.py` via a separate Control Lane Issue and review.

See `sample_output.md` for captured results from the sample dataset.
