"""Config tests for the TqSdk adapter skeleton."""

import pytest

from option_quant_fund.data.sources.tq.config import ENV_TQ_PASS
from option_quant_fund.data.sources.tq.config import ENV_TQ_USER
from option_quant_fund.data.sources.tq.config import TqConfig
from option_quant_fund.data.sources.tq.config import TqConfigError
from option_quant_fund.data.sources.tq.config import check_env


def test_check_env_when_vars_are_absent(monkeypatch):
    monkeypatch.delenv(ENV_TQ_USER, raising=False)
    monkeypatch.delenv(ENV_TQ_PASS, raising=False)

    status = check_env()

    assert status.user_present is False
    assert status.password_present is False
    assert status.complete is False
    assert status.missing == (ENV_TQ_USER, ENV_TQ_PASS)


def test_check_env_when_vars_are_set(monkeypatch):
    monkeypatch.setenv(ENV_TQ_USER, "fake_user")
    monkeypatch.setenv(ENV_TQ_PASS, "fake_pass")

    status = check_env()

    assert status.complete is True
    assert status.missing == ()


def test_from_env_raises_for_missing_vars(monkeypatch):
    monkeypatch.delenv(ENV_TQ_USER, raising=False)
    monkeypatch.delenv(ENV_TQ_PASS, raising=False)

    with pytest.raises(
        TqConfigError,
        match="Missing required TqSdk environment variable",
    ):
        TqConfig.from_env()


def test_from_env_raises_for_missing_password(monkeypatch):
    monkeypatch.setenv(ENV_TQ_USER, "fake_user")
    monkeypatch.delenv(ENV_TQ_PASS, raising=False)

    with pytest.raises(TqConfigError, match=ENV_TQ_PASS):
        TqConfig.from_env()


def test_from_env_reads_fake_environment(monkeypatch):
    monkeypatch.setenv(ENV_TQ_USER, "fake_user")
    monkeypatch.setenv(ENV_TQ_PASS, "fake_pass")

    config = TqConfig.from_env()

    assert config.user == "fake_user"
    assert config.password == "fake_pass"


def test_from_env_accepts_explicit_mapping():
    mapping = {
        ENV_TQ_USER: "local_user",
        ENV_TQ_PASS: "local_pass",
    }

    config = TqConfig.from_env(environ=mapping)

    assert config.user == "local_user"
    assert config.password == "local_pass"


def test_from_env_rejects_blank_user_value(monkeypatch):
    monkeypatch.setenv(ENV_TQ_USER, "")
    monkeypatch.setenv(ENV_TQ_PASS, "fake_pass")

    with pytest.raises(TqConfigError, match=ENV_TQ_USER):
        TqConfig.from_env()
