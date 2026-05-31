"""Fast Lane prototype: minimal option chain builder from sample quotes."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from option_quant_fund.data.loader import load_option_quotes

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SAMPLE_PATH = PROJECT_ROOT / "data" / "sample" / "option_quotes_sample.csv"


def _quote_row_to_dict(row: pd.Series) -> dict[str, Any]:
    return {
        "option_symbol": row["option_symbol"],
        "bid_price": float(row["bid_price"]),
        "ask_price": float(row["ask_price"]),
        "last_price": float(row["last_price"]),
        "volume": int(row["volume"]),
        "open_interest": int(row["open_interest"]),
    }


def build_option_chain(quotes: pd.DataFrame) -> dict[str, dict[float, dict[str, dict[str, Any]]]]:
    """Build nested chain: expiry -> strike -> option_type -> quote fields."""
    chain: dict[str, dict[float, dict[str, dict[str, Any]]]] = {}

    for expiry, expiry_df in quotes.groupby("expiry", sort=True):
        expiry_key = pd.Timestamp(expiry).strftime("%Y-%m-%d")
        strikes: dict[float, dict[str, dict[str, Any]]] = {}

        for strike, strike_df in expiry_df.groupby("strike", sort=True):
            legs: dict[str, dict[str, Any]] = {}
            for _, row in strike_df.iterrows():
                legs[str(row["option_type"])] = _quote_row_to_dict(row)
            strikes[float(strike)] = legs

        chain[expiry_key] = strikes

    return chain


def build_summary_dataframe(quotes: pd.DataFrame) -> pd.DataFrame:
    """Summarize call/put availability and top-of-book prices per expiry/strike."""
    rows: list[dict[str, Any]] = []

    for expiry, expiry_df in quotes.groupby("expiry", sort=True):
        expiry_key = pd.Timestamp(expiry).strftime("%Y-%m-%d")
        for strike, strike_df in expiry_df.groupby("strike", sort=True):
            call = strike_df[strike_df["option_type"] == "C"]
            put = strike_df[strike_df["option_type"] == "P"]
            rows.append(
                {
                    "expiry": expiry_key,
                    "strike": float(strike),
                    "has_call": not call.empty,
                    "has_put": not put.empty,
                    "call_bid": float(call["bid_price"].iloc[0]) if not call.empty else None,
                    "call_ask": float(call["ask_price"].iloc[0]) if not call.empty else None,
                    "put_bid": float(put["bid_price"].iloc[0]) if not put.empty else None,
                    "put_ask": float(put["ask_price"].iloc[0]) if not put.empty else None,
                }
            )

    return pd.DataFrame(rows)


def format_chain_report(chain: dict, summary: pd.DataFrame) -> str:
    lines = ["Option Chain Prototype Report", "=" * 32, ""]
    lines.append(f"Expiries: {len(chain)}")
    for expiry, strikes in chain.items():
        lines.append(f"\nExpiry {expiry} — {len(strikes)} strike(s)")
        for strike, legs in strikes.items():
            call_flag = "C" if "C" in legs else "-"
            put_flag = "P" if "P" in legs else "-"
            lines.append(f"  strike {strike:g}: Call={call_flag} Put={put_flag}")
    lines.append("\nSummary DataFrame:")
    lines.append(summary.to_string(index=False))
    return "\n".join(lines)


def run_prototype(sample_path: Path | str | None = None) -> tuple[dict, pd.DataFrame]:
    path = Path(sample_path) if sample_path else DEFAULT_SAMPLE_PATH
    quotes = load_option_quotes(str(path))
    chain = build_option_chain(quotes)
    summary = build_summary_dataframe(quotes)
    return chain, summary


def main() -> None:
    chain, summary = run_prototype()
    print(format_chain_report(chain, summary))


if __name__ == "__main__":
    main()
