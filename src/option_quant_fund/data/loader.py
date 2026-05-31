"""Minimal CSV data loaders for option and underlying quotes."""

from __future__ import annotations

import pandas as pd

OPTION_QUOTE_COLUMNS = [
    "timestamp",
    "underlying_symbol",
    "option_symbol",
    "expiry",
    "strike",
    "option_type",
    "bid_price",
    "ask_price",
    "last_price",
    "volume",
    "open_interest",
    "underlying_price",
]

UNDERLYING_QUOTE_COLUMNS = [
    "timestamp",
    "underlying_symbol",
    "last_price",
    "bid_price",
    "ask_price",
    "volume",
]

VALID_OPTION_TYPES = {"C", "P"}


def _require_columns(df: pd.DataFrame, required: list[str]) -> None:
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def _validate_option_types(df: pd.DataFrame) -> None:
    invalid = ~df["option_type"].isin(VALID_OPTION_TYPES)
    if invalid.any():
        values = sorted(df.loc[invalid, "option_type"].astype(str).unique())
        raise ValueError(f"Invalid option_type values: {values}")


def load_option_quotes(path: str) -> pd.DataFrame:
    """Load option quote CSV into a typed DataFrame."""
    df = pd.read_csv(path)
    _require_columns(df, OPTION_QUOTE_COLUMNS)

    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["expiry"] = pd.to_datetime(df["expiry"]).dt.normalize()

    numeric_columns = [
        "strike",
        "bid_price",
        "ask_price",
        "last_price",
        "underlying_price",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column])

    df["volume"] = pd.to_numeric(df["volume"], downcast="integer").astype(int)
    df["open_interest"] = pd.to_numeric(df["open_interest"], downcast="integer").astype(int)
    _validate_option_types(df)

    return df


def load_underlying_quotes(path: str) -> pd.DataFrame:
    """Load underlying quote CSV into a typed DataFrame."""
    df = pd.read_csv(path)
    _require_columns(df, UNDERLYING_QUOTE_COLUMNS)

    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    for column in ("last_price", "bid_price", "ask_price"):
        df[column] = pd.to_numeric(df[column])

    df["volume"] = pd.to_numeric(df["volume"], downcast="integer").astype(int)

    return df


class DataLoader:
    """Backward-compatible wrapper around module-level loaders."""

    def load_option_quotes(self, path: str) -> pd.DataFrame:
        return load_option_quotes(path)

    def load_underlying_quotes(self, path: str) -> pd.DataFrame:
        return load_underlying_quotes(path)

    def load(self, path: str) -> None:
        """Legacy placeholder entry point from TASK-001."""
        raise NotImplementedError("Use load_option_quotes() or load_underlying_quotes().")
