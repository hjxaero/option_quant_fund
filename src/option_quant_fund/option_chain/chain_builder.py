"""Minimal formal option chain builder (Control Lane / TASK-004)."""

from __future__ import annotations

from typing import Any

import pandas as pd

REQUIRED_COLUMNS = [
    "expiry",
    "strike",
    "option_type",
    "option_symbol",
    "bid_price",
    "ask_price",
    "last_price",
    "volume",
    "open_interest",
]

VALID_OPTION_TYPES = {"C", "P"}


def _require_columns(df: pd.DataFrame) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def _validate_option_types(df: pd.DataFrame) -> None:
    invalid = ~df["option_type"].isin(VALID_OPTION_TYPES)
    if invalid.any():
        values = sorted(df.loc[invalid, "option_type"].astype(str).unique())
        raise ValueError(f"Invalid option_type values: {values}")


def _quote_row_to_dict(row: pd.Series) -> dict[str, Any]:
    return {
        "option_symbol": row["option_symbol"],
        "bid_price": float(row["bid_price"]),
        "ask_price": float(row["ask_price"]),
        "last_price": float(row["last_price"]),
        "volume": int(row["volume"]),
        "open_interest": int(row["open_interest"]),
    }


def build_option_chain(
    option_quotes: pd.DataFrame,
) -> dict[str, dict[float, dict[str, dict[str, Any]]]]:
    """Build nested option chain: expiry -> strike -> option_type -> quote dict."""
    _require_columns(option_quotes)
    _validate_option_types(option_quotes)

    chain: dict[str, dict[float, dict[str, dict[str, Any]]]] = {}

    for expiry, expiry_df in option_quotes.groupby("expiry", sort=True):
        expiry_key = pd.Timestamp(expiry).strftime("%Y-%m-%d")
        strikes: dict[float, dict[str, dict[str, Any]]] = {}

        for strike, strike_df in expiry_df.groupby("strike", sort=True):
            legs: dict[str, dict[str, Any]] = {}
            for _, row in strike_df.iterrows():
                legs[str(row["option_type"])] = _quote_row_to_dict(row)
            strikes[float(strike)] = legs

        chain[expiry_key] = strikes

    return chain


def summarize_option_chain(
    option_chain: dict[str, dict[float, dict[str, dict[str, Any]]]],
) -> pd.DataFrame:
    """Summarize call/put availability and top-of-book prices per expiry/strike."""
    rows: list[dict[str, Any]] = []

    for expiry in sorted(option_chain):
        for strike in sorted(option_chain[expiry]):
            legs = option_chain[expiry][strike]
            call = legs.get("C")
            put = legs.get("P")
            rows.append(
                {
                    "expiry": expiry,
                    "strike": float(strike),
                    "has_call": call is not None,
                    "has_put": put is not None,
                    "call_bid": call["bid_price"] if call else None,
                    "call_ask": call["ask_price"] if call else None,
                    "put_bid": put["bid_price"] if put else None,
                    "put_ask": put["ask_price"] if put else None,
                }
            )

    return pd.DataFrame(rows)


class ChainBuilder:
    """Backward-compatible wrapper around module-level builders."""

    def build(self, option_quotes: pd.DataFrame) -> dict[str, dict[float, dict[str, dict[str, Any]]]]:
        return build_option_chain(option_quotes)

    def summarize(
        self,
        option_chain: dict[str, dict[float, dict[str, dict[str, Any]]]],
    ) -> pd.DataFrame:
        return summarize_option_chain(option_chain)
