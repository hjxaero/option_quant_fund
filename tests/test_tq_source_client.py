"""Client tests for the TqSdk adapter skeleton."""

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


def test_import_tq_subpackage():
    from option_quant_fund.data.sources import tq

    assert hasattr(tq, "TqClient")
    assert hasattr(tq, "TqConfig")


def test_client_starts_disconnected(monkeypatch):
    monkeypatch.setenv(ENV_TQ_USER, "fake_user")
    monkeypatch.setenv(ENV_TQ_PASS, "fake_pass")

    client = TqClient.from_env()

    assert client.is_connected is False
    assert client.config.user == "fake_user"


def test_connect_without_tqsdk_raises(monkeypatch):
    monkeypatch.setenv(ENV_TQ_USER, "fake_user")
    monkeypatch.setenv(ENV_TQ_PASS, "fake_pass")
    monkeypatch.setitem(sys.modules, "tqsdk", None)

    client = TqClient.from_env()

    with pytest.raises(TqSdkNotInstalledError, match="tqsdk is not installed"):
        client.connect()


def test_connect_with_stubbed_tqsdk(monkeypatch):
    monkeypatch.setenv(ENV_TQ_USER, "fake_user")
    monkeypatch.setenv(ENV_TQ_PASS, "fake_pass")

    api = MagicMock()
    auth = MagicMock()
    stub = ModuleType("tqsdk")
    stub.TqApi = MagicMock(return_value=api)
    stub.TqAuth = auth
    monkeypatch.setitem(sys.modules, "tqsdk", stub)

    client = TqClient.from_env()
    client.connect()

    auth.assert_called_once_with("fake_user", "fake_pass")
    stub.TqApi.assert_called_once()
    assert client.is_connected is True

    client.close()
    api.close.assert_called_once()
    assert client.is_connected is False


def test_context_manager_calls_close(monkeypatch):
    monkeypatch.setenv(ENV_TQ_USER, "fake_user")
    monkeypatch.setenv(ENV_TQ_PASS, "fake_pass")

    api = MagicMock()
    stub = ModuleType("tqsdk")
    stub.TqApi = MagicMock(return_value=api)
    stub.TqAuth = MagicMock()
    monkeypatch.setitem(sys.modules, "tqsdk", stub)

    config = TqConfig.from_env()
    with TqClient(config, auto_connect=True) as client:
        assert client.is_connected is True

    api.close.assert_called_once()


@pytest.mark.skipif(
    is_tqsdk_available(),
    reason="skip when tqsdk is installed",
)
def test_is_tqsdk_available_without_package():
    assert is_tqsdk_available() is False
