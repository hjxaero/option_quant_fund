"""Unit tests for TqSdk client skeleton."""

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


def test_sources_tq_package_exports():
    from option_quant_fund.data.sources import tq

    assert hasattr(tq, "TqClient")
    assert hasattr(tq, "TqConfig")


def test_from_env_client_stays_offline(monkeypatch):
    monkeypatch.setenv(ENV_TQ_USER, "fake_user")
    monkeypatch.setenv(ENV_TQ_PASS, "fake_pass")

    client = TqClient.from_env()

    assert client.is_connected is False
    assert client.config.user == "fake_user"


def test_connect_requires_installed_tqsdk(monkeypatch):
    monkeypatch.setenv(ENV_TQ_USER, "fake_user")
    monkeypatch.setenv(ENV_TQ_PASS, "fake_pass")
    monkeypatch.setitem(sys.modules, "tqsdk", None)

    client = TqClient.from_env()

    with pytest.raises(TqSdkNotInstalledError, match="tqsdk is not installed"):
        client.connect()


def test_connect_with_mocked_tqsdk_module(monkeypatch):
    monkeypatch.setenv(ENV_TQ_USER, "fake_user")
    monkeypatch.setenv(ENV_TQ_PASS, "fake_pass")

    mock_api = MagicMock()
    mock_auth = MagicMock()
    fake_module = ModuleType("tqsdk")
    fake_module.TqApi = MagicMock(return_value=mock_api)
    fake_module.TqAuth = mock_auth
    monkeypatch.setitem(sys.modules, "tqsdk", fake_module)

    client = TqClient.from_env()
    client.connect()

    mock_auth.assert_called_once_with("fake_user", "fake_pass")
    fake_module.TqApi.assert_called_once()
    assert client.is_connected is True

    client.close()
    mock_api.close.assert_called_once()
    assert client.is_connected is False


def test_context_manager_closes_session(monkeypatch):
    monkeypatch.setenv(ENV_TQ_USER, "fake_user")
    monkeypatch.setenv(ENV_TQ_PASS, "fake_pass")

    mock_api = MagicMock()
    fake_module = ModuleType("tqsdk")
    fake_module.TqApi = MagicMock(return_value=mock_api)
    fake_module.TqAuth = MagicMock()
    monkeypatch.setitem(sys.modules, "tqsdk", fake_module)

    config = TqConfig.from_env()
    with TqClient(config, auto_connect=True) as client:
        assert client.is_connected is True

    mock_api.close.assert_called_once()


@pytest.mark.skipif(
    is_tqsdk_available(),
    reason="only run when tqsdk is absent",
)
def test_is_tqsdk_available_false_without_package():
    assert is_tqsdk_available() is False
