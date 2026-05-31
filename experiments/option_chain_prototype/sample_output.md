# Sample Output — Option Chain Prototype

## Input

- **Source:** `data/sample/option_quotes_sample.csv`
- **Loader:** `load_option_quotes()` from `src/option_quant_fund/data/loader.py`
- **Rows:** 5 simulated option quotes (underlying `IM`)

## Built Expiries

| Expiry | Strike count | Notes |
|--------|--------------|-------|
| 2025-01-17 | 2 | Strikes 4800, 5000 |
| 2025-02-21 | 2 | Strikes 5000, 5200 |

## Call / Put Coverage

| Expiry | Strike | Has Call | Has Put |
|--------|--------|----------|---------|
| 2025-01-17 | 4800 | Yes | Yes |
| 2025-01-17 | 5000 | Yes | No |
| 2025-02-21 | 5000 | Yes | No |
| 2025-02-21 | 5200 | No | Yes |

Across the full sample, both **Call** and **Put** legs appear; individual strikes may have only one side.

## Console Report (captured)

```
Option Chain Prototype Report
================================

Expiries: 2

Expiry 2025-01-17 — 2 strike(s)
  strike 4800: Call=C Put=P
  strike 5000: Call=C Put=-

Expiry 2025-02-21 — 2 strike(s)
  strike 5000: Call=C Put=-
  strike 5200: Call=- Put=P

Summary DataFrame:
    expiry  strike  has_call  has_put  call_bid  call_ask  put_bid  put_ask
2025-01-17  4800.0      True     True     120.5     122.0     18.0     19.5
2025-01-17  5000.0      True    False      45.0      46.5      NaN      NaN
2025-02-21  5000.0      True    False      88.0      90.0      NaN      NaN
2025-02-21  5200.0     False     True       NaN       NaN     95.0     97.0
```

## Conclusion

The TASK-002 sample schema is **sufficient** for a minimal option chain prototype:

- Grouping by `expiry` works
- Sorting by `strike` works
- Call/Put separation via `option_type` works
- Summary fields (`has_call`, `has_put`, bid/ask) support quick inspection

**Recommendation:** Proceed to Control Lane to formalize this structure in `src/option_quant_fund/option_chain/chain_builder.py` (separate Issue), without changing this Fast Lane experiment.
