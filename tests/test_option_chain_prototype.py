"""Smoke tests for Fast Lane option chain prototype (TASK-003)."""

from pathlib import Path

import pytest

from experiments.option_chain_prototype.prototype_option_chain import (
    DEFAULT_SAMPLE_PATH,
    build_option_chain,
    build_summary_dataframe,
    run_prototype,
)
from option_quant_fund.data.loader import load_option_quotes

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "sample" / "option_quotes_sample.csv"


@pytest.fixture
def quotes():
    return load_option_quotes(str(SAMPLE))


def test_run_prototype_returns_non_empty_chain():
    chain, summary = run_prototype(SAMPLE)
    assert chain
    assert not summary.empty


def test_at_least_one_expiry(quotes):
    chain = build_option_chain(quotes)
    assert len(chain) >= 1


def test_has_call_and_put_legs(quotes):
    chain = build_option_chain(quotes)
    all_types = {
        opt_type
        for strikes in chain.values()
        for legs in strikes.values()
        for opt_type in legs
    }
    assert "C" in all_types
    assert "P" in all_types


def test_strikes_sorted_within_expiry(quotes):
    chain = build_option_chain(quotes)
    for strikes in chain.values():
        strike_keys = list(strikes.keys())
        assert strike_keys == sorted(strike_keys)


def test_summary_columns(quotes):
    summary = build_summary_dataframe(quotes)
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


def test_default_sample_path_exists():
    assert DEFAULT_SAMPLE_PATH.is_file()
