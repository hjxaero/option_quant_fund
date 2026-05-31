"""Tests for minimal CSV data loaders (TASK-002)."""

from pathlib import Path

import pandas as pd
import pytest

from option_quant_fund.data.loader import (
    OPTION_QUOTE_COLUMNS,
    UNDERLYING_QUOTE_COLUMNS,
    load_option_quotes,
    load_underlying_quotes,
)

ROOT = Path(__file__).resolve().parents[1]
OPTION_SAMPLE = ROOT / "data" / "sample" / "option_quotes_sample.csv"
UNDERLYING_SAMPLE = ROOT / "data" / "sample" / "underlying_quotes_sample.csv"


def test_load_option_quotes_reads_sample_file():
    df = load_option_quotes(str(OPTION_SAMPLE))
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 2


def test_load_underlying_quotes_reads_sample_file():
    df = load_underlying_quotes(str(UNDERLYING_SAMPLE))
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 2


def test_option_quotes_has_required_columns():
    df = load_option_quotes(str(OPTION_SAMPLE))
    assert list(df.columns) == OPTION_QUOTE_COLUMNS


def test_underlying_quotes_has_required_columns():
    df = load_underlying_quotes(str(UNDERLYING_SAMPLE))
    assert list(df.columns) == UNDERLYING_QUOTE_COLUMNS


def test_option_quotes_timestamp_parsed():
    df = load_option_quotes(str(OPTION_SAMPLE))
    assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])
    assert pd.api.types.is_datetime64_any_dtype(df["expiry"])


def test_underlying_quotes_timestamp_parsed():
    df = load_underlying_quotes(str(UNDERLYING_SAMPLE))
    assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])


def test_option_type_values_are_valid():
    df = load_option_quotes(str(OPTION_SAMPLE))
    assert set(df["option_type"].unique()) <= {"C", "P"}


def test_bid_price_less_than_ask_price():
    options = load_option_quotes(str(OPTION_SAMPLE))
    underlying = load_underlying_quotes(str(UNDERLYING_SAMPLE))
    assert (options["bid_price"] < options["ask_price"]).all()
    assert (underlying["bid_price"] < underlying["ask_price"]).all()


def test_missing_required_option_columns_raises(tmp_path):
    bad_file = tmp_path / "bad_option.csv"
    bad_file.write_text("timestamp,underlying_symbol\n2025-01-02 09:31:00,IM\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Missing required columns"):
        load_option_quotes(str(bad_file))


def test_missing_required_underlying_columns_raises(tmp_path):
    bad_file = tmp_path / "bad_underlying.csv"
    bad_file.write_text("timestamp,underlying_symbol\n2025-01-02 09:31:00,IM\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Missing required columns"):
        load_underlying_quotes(str(bad_file))


def test_invalid_option_type_raises(tmp_path):
    header = ",".join(OPTION_QUOTE_COLUMNS)
    row = "2025-01-02 09:31:00,IM,IM2501-X-5000,2025-01-17,5000,X,1.0,2.0,1.5,10,100,5100.0"
    bad_file = tmp_path / "bad_type.csv"
    bad_file.write_text(f"{header}\n{row}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid option_type"):
        load_option_quotes(str(bad_file))
