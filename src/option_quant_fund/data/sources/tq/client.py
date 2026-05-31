"""Offline-first TqSdk client skeleton."""

from __future__ import annotations

from typing import Any

from option_quant_fund.data.sources.tq.config import TqConfig


class TqSdkNotInstalledError(ImportError):
    """The optional tqsdk package is not available."""


def is_tqsdk_available() -> bool:
    """Return True when tqsdk can be imported."""
    try:
        import tqsdk  # noqa: F401
    except ImportError:
        return False
    return True


class TqClient:
    """Thin wrapper around future TqSdk usage.

    TASK-007 only defines structure and credential wiring.
    Download logic arrives in TASK-008.
    """

    def __init__(
        self,
        config: TqConfig,
        *,
        auto_connect: bool = False,
    ) -> None:
        self._config = config
        self._api: Any | None = None
        self._connected = False
        if auto_connect:
            self.connect()

    @classmethod
    def from_env(cls, *, auto_connect: bool = False) -> TqClient:
        config = TqConfig.from_env()
        return cls(config, auto_connect=auto_connect)

    @property
    def config(self) -> TqConfig:
        return self._config

    @property
    def is_connected(self) -> bool:
        return self._connected

    def connect(self) -> None:
        """Create a live TqSdk session when explicitly requested."""
        if self._connected:
            return

        if not is_tqsdk_available():
            raise TqSdkNotInstalledError(
                "tqsdk is not installed; install it locally before connect()"
            )

        from tqsdk import TqApi
        from tqsdk import TqAuth

        auth = TqAuth(
            self._config.user,
            self._config.password,
        )
        self._api = TqApi(auth=auth)
        self._connected = True

    def close(self) -> None:
        if self._api is not None:
            self._api.close()
            self._api = None
        self._connected = False

    def __enter__(self) -> TqClient:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
