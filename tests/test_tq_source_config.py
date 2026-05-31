"""Unit tests for TqSdk configuration skeleton."""

import pytest

from option_quant_fund.data.sources.tq.config import ENV_TQ_PASS
from option_quant_fund.data.sources.tq.config import ENV_TQ_USER
from option_quant_fund.data.sources.tq.config import TqConfig
from option_quant_fund.data.sources.tq.config import TqConfigError
from option_quant_fund.data.sources.tq.config import check_env


def test_check_env_missing_when_vars_absent(monkeypatch):
    monkeypatch.delenv(ENV_TQ_USER, raising=False)
    monkeypatch.delenv(ENV_TQ_PASS, raising=False)

    status = check_env()

    assert status.user_present is False
    assert status.password_present is False
    assert status.complete is False
    assert status.missing == (ENV_TQ_USER, ENV_TQ_PASS)


def test_check_env_complete_with_fake_vars(monkeypatch):
    monkeypatch.setenv(ENV_TQ_USER, "fake_user")
    monkeypatch.setenv(ENV_TQ_PASS, "fake_pass")

    status = check_env()

    assert status.complete is True
    assert status.missing == ()


def test_from_env_error_when_vars_missing(monkeypatch):
    monkeypatch.delenv(ENV_TQ_USER, raising=False)
    monkeypatch.delenv(ENV_TQ_PASS, raising=False)

    with pytest.raises(
        TqConfigError,
        match="Missing required TqSdk environment variable",
    ):
        TqConfig.from_env()


def test_from_env_error_when_password_missing(monkeypatch):
    monkeypatch.setenv(ENV_TQ_USER, "fake_user")
    monkeypatch.delenv(ENV_TQ_PASS, raising=False)

    with pytest.raises(TqConfigError, match=ENV_TQ_PASS):
        TqConfig.from_env()


def test_from_env_reads_fake_vars(monkeypatch):
    monkeypatch.setenv(ENV_TQ_USER, "fake_user")
    monkeypatch.setenv(ENV_TQ_PASS, "fake_pass")

    config = TqConfig.from_env()

    assert config.user == "fake_user"
    assert config.password == "fake_pass"


def test_from_env_accepts_custom_environ_dict():
    custom = {
        ENV_TQ_USER: "scoped_user",
        ENV_TQ_PASS: "scoped_pass",
    }

    config = TqConfig.from_env(environ=custom)

    assert config.user == "scoped_user"
    assert config.password == "scoped_pass"


def test_from_env_rejects_blank_username(monkeypatch):
    monkeypatch.setenv(ENV_TQ_USER, "")
    monkeypatch.setenv(ENV_TQ_PASS, "fake_pass")

    with pytest.raises(TqConfigError, match=ENV_TQ_USER):
        TqConfig.from_env()
