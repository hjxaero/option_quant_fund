"""Offline tests for TqSdk client skeleton."""

import sys
from types import ModuleType
from unittest.mock import MagicMock

import pytest

from option_quant_fund.data.sources.tq.client import TqClient
from option_quant_fund.data.sources.tq.client import TqSdkNotInstalledError
from option_quant_fund.data.sources.tq.client import is_tqsdk_available
from option_quant_fund.data.sources.tq.config import ENV_TQ_PASS
from option_quant_fund.data.sources.tq.config import ENV_TQ_USER
from option_quant_fund.data.sources.tq.config import TqConfig


def test_tq_subpackage_exports():
    from option_quant_fund.data.sources import tq

    assert hasattr(tq, "TqClient")
    assert hasattr(tq, "TqConfig")


def test_new_client_is_offline_by_default(monkeypatch):
    monkeypatch.setenv(ENV_TQ_USER, "fake_user")
    monkeypatch.setenv(ENV_TQ_PASS, "fake_pass")

    client = TqClient.from_env()

    assert client.is_connected is False
    assert client.config.user == "fake_user"


def test_connect_errors_when_tqsdk_missing(monkeypatch):
    monkeypatch.setenv(ENV_TQ_USER, "fake_user")
    monkeypatch.setenv(ENV_TQ_PASS, "fake_pass")
    monkeypatch.setitem(sys.modules, "tqsdk", None)

    client = TqClient.from_env()

    with pytest.raises(TqSdkNotInstalledError, match="tqsdk is not installed"):
        client.connect()


def test_connect_builds_session_with_mock_module(monkeypatch):
    monkeypatch.setenv(ENV_TQ_USER, "fake_user")
    monkeypatch.setenv(ENV_TQ_PASS, "fake_pass")

    api = MagicMock()
    auth_ctor = MagicMock()
    stub = ModuleType("tqsdk")
    stub.TqApi = MagicMock(return_value=api)
    stub.TqAuth = auth_ctor
    monkeypatch.setitem(sys.modules, "tqsdk", stub)

    client = TqClient.from_env()
    client.connect()

    auth_ctor.assert_called_once_with("fake_user", "fake_pass")
    stub.TqApi.assert_called_once()
    assert client.is_connected is True

    client.close()
    api.close.assert_called_once()
    assert client.is_connected is False


def test_client_context_manager_closes_api(monkeypatch):
    monkeypatch.setenv(ENV_TQ_USER, "fake_user")
    monkeypatch.setenv(ENV_TQ_PASS, "fake_pass")

    api = MagicMock()
    stub = ModuleType("tqsdk")
    stub.TqApi = MagicMock(return_value=api)
    stub.TqAuth = MagicMock()
    monkeypatch.setitem(sys.modules, "tqsdk", stub)

    cfg = TqConfig.from_env()
    with TqClient(cfg, auto_connect=True) as client:
        assert client.is_connected is True

    api.close.assert_called_once()


@pytest.mark.skipif(
    is_tqsdk_available(),
    reason="requires tqsdk to be absent",
)
def test_is_tqsdk_available_reports_false():
    assert is_tqsdk_available() is False
