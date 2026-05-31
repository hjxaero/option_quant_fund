"""Offline tests for TqSdk configuration helpers."""

import pytest

from option_quant_fund.data.sources.tq.config import ENV_TQ_PASS
from option_quant_fund.data.sources.tq.config import ENV_TQ_USER
from option_quant_fund.data.sources.tq.config import TqConfig
from option_quant_fund.data.sources.tq.config import TqConfigError
from option_quant_fund.data.sources.tq.config import check_env


def test_check_env_flags_missing_variables(monkeypatch):
    monkeypatch.delenv(ENV_TQ_USER, raising=False)
    monkeypatch.delenv(ENV_TQ_PASS, raising=False)

    result = check_env()

    assert result.user_present is False
    assert result.password_present is False
    assert result.complete is False
    assert result.missing == (ENV_TQ_USER, ENV_TQ_PASS)


def test_check_env_flags_present_variables(monkeypatch):
    monkeypatch.setenv(ENV_TQ_USER, "fake_user")
    monkeypatch.setenv(ENV_TQ_PASS, "fake_pass")

    result = check_env()

    assert result.complete is True
    assert result.missing == ()


def test_from_env_raises_without_credentials(monkeypatch):
    monkeypatch.delenv(ENV_TQ_USER, raising=False)
    monkeypatch.delenv(ENV_TQ_PASS, raising=False)

    with pytest.raises(
        TqConfigError,
        match="Missing required TqSdk environment variable",
    ):
        TqConfig.from_env()


def test_from_env_raises_without_password(monkeypatch):
    monkeypatch.setenv(ENV_TQ_USER, "fake_user")
    monkeypatch.delenv(ENV_TQ_PASS, raising=False)

    with pytest.raises(TqConfigError, match=ENV_TQ_PASS):
        TqConfig.from_env()


def test_from_env_builds_config_from_fake_vars(monkeypatch):
    monkeypatch.setenv(ENV_TQ_USER, "fake_user")
    monkeypatch.setenv(ENV_TQ_PASS, "fake_pass")

    config = TqConfig.from_env()

    assert config.user == "fake_user"
    assert config.password == "fake_pass"


def test_from_env_reads_passed_mapping():
    mapping = {
        ENV_TQ_USER: "scoped_user",
        ENV_TQ_PASS: "scoped_pass",
    }

    config = TqConfig.from_env(environ=mapping)

    assert config.user == "scoped_user"
    assert config.password == "scoped_pass"


def test_from_env_rejects_empty_user(monkeypatch):
    monkeypatch.setenv(ENV_TQ_USER, "")
    monkeypatch.setenv(ENV_TQ_PASS, "fake_pass")

    with pytest.raises(TqConfigError, match=ENV_TQ_USER):
        TqConfig.from_env()
