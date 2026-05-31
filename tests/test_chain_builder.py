"""Unit tests for formal option chain builder (TASK-004)."""

from pathlib import Path

import pandas as pd
import pytest

from option_quant_fund.data.loader import load_option_quotes
from option_quant_fund.option_chain.chain_builder import (
    REQUIRED_COLUMNS,
    build_option_chain,
    summarize_option_chain,
)

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "sample" / "option_quotes_sample.csv"


@pytest.fixture
def quotes():
    return load_option_quotes(str(SAMPLE))


def test_load_sample_and_build_chain(quotes):
    chain = build_option_chain(quotes)
    assert chain


def test_chain_has_at_least_one_expiry(quotes):
    chain = build_option_chain(quotes)
    assert len(chain) >= 1


def test_strikes_sorted_within_expiry(quotes):
    chain = build_option_chain(quotes)
    for strikes in chain.values():
        assert list(strikes.keys()) == sorted(strikes.keys())


def test_chain_has_call_and_put_legs(quotes):
    chain = build_option_chain(quotes)
    all_types = {
        opt_type
        for strikes in chain.values()
        for legs in strikes.values()
        for opt_type in legs
    }
    assert "C" in all_types
    assert "P" in all_types


def test_strike_legs_distinguish_call_and_put(quotes):
    chain = build_option_chain(quotes)
    both_sides = [
        legs
        for strikes in chain.values()
        for legs in strikes.values()
        if "C" in legs and "P" in legs
    ]
    assert both_sides
    sample = both_sides[0]
    assert sample["C"]["option_symbol"] != sample["P"]["option_symbol"]


def test_missing_required_columns_raises(quotes):
    bad = quotes.drop(columns=["strike"])
    with pytest.raises(ValueError, match="Missing required columns"):
        build_option_chain(bad)


def test_invalid_option_type_raises(quotes):
    bad = quotes.copy()
    bad.loc[bad.index[0], "option_type"] = "X"
    with pytest.raises(ValueError, match="Invalid option_type"):
        build_option_chain(bad)


def test_summarize_returns_dataframe(quotes):
    chain = build_option_chain(quotes)
    summary = summarize_option_chain(chain)
    assert isinstance(summary, pd.DataFrame)
    assert not summary.empty


def test_summarize_has_required_columns(quotes):
    chain = build_option_chain(quotes)
    summary = summarize_option_chain(chain)
    expected = {
        "expiry",
        "strike",
        "has_call",
        "has_put",
        "call_bid",
        "call_ask",
        "put_bid",
        "put_ask",
    }
    assert expected.issubset(set(summary.columns))


def test_required_columns_constant_matches_builder():
    assert "expiry" in REQUIRED_COLUMNS
    assert "option_type" in REQUIRED_COLUMNS
