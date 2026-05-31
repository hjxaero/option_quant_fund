"""Tests for TqSdk client skeleton (TASK-007)."""

import sys
from types import ModuleType
from unittest.mock import MagicMock

import pytest

from option_quant_fund.data.sources.tq.client import (
    TqClient,
    TqSdkNotInstalledError,
    is_tqsdk_available,
)
from option_quant_fund.data.sources.tq.config import ENV_TQ_PASS, ENV_TQ_USER, TqConfig


def test_tq_package_imports_without_tqsdk_installed():
    from option_quant_fund.data.sources import tq

    assert hasattr(tq, "TqClient")
    assert hasattr(tq, "TqConfig")


def test_client_from_env_is_not_connected_by_default(monkeypatch):
    monkeypatch.setenv(ENV_TQ_USER, "fake_user")
    monkeypatch.setenv(ENV_TQ_PASS, "fake_pass")

    client = TqClient.from_env()

    assert client.is_connected is False
    assert client.config.user == "fake_user"


def test_connect_raises_when_tqsdk_not_installed(monkeypatch):
    monkeypatch.setenv(ENV_TQ_USER, "fake_user")
    monkeypatch.setenv(ENV_TQ_PASS, "fake_pass")
    monkeypatch.setitem(sys.modules, "tqsdk", None)

    client = TqClient.from_env()

    with pytest.raises(TqSdkNotInstalledError, match="tqsdk is not installed"):
        client.connect()


def test_connect_uses_fake_env_with_mocked_tqsdk(monkeypatch):
    monkeypatch.setenv(ENV_TQ_USER, "fake_user")
    monkeypatch.setenv(ENV_TQ_PASS, "fake_pass")

    mock_api = MagicMock()
    mock_auth = MagicMock()
    fake_tqsdk = ModuleType("tqsdk")
    fake_tqsdk.TqApi = MagicMock(return_value=mock_api)
    fake_tqsdk.TqAuth = mock_auth
    monkeypatch.setitem(sys.modules, "tqsdk", fake_tqsdk)

    client = TqClient.from_env()
    client.connect()

    mock_auth.assert_called_once_with("fake_user", "fake_pass")
    fake_tqsdk.TqApi.assert_called_once()
    assert client.is_connected is True

    client.close()
    mock_api.close.assert_called_once()
    assert client.is_connected is False


def test_context_manager_closes_client(monkeypatch):
    monkeypatch.setenv(ENV_TQ_USER, "fake_user")
    monkeypatch.setenv(ENV_TQ_PASS, "fake_pass")

    mock_api = MagicMock()
    fake_tqsdk = ModuleType("tqsdk")
    fake_tqsdk.TqApi = MagicMock(return_value=mock_api)
    fake_tqsdk.TqAuth = MagicMock()
    monkeypatch.setitem(sys.modules, "tqsdk", fake_tqsdk)

    config = TqConfig.from_env()
    with TqClient(config, auto_connect=True) as client:
        assert client.is_connected is True

    mock_api.close.assert_called_once()


@pytest.mark.skipif(is_tqsdk_available(), reason="offline test only when tqsdk absent")
def test_is_tqsdk_available_false_when_not_installed():
    assert is_tqsdk_available() is False
