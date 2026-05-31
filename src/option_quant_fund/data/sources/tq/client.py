"""TqSdk client wrapper skeleton for TASK-007."""

from __future__ import annotations

from typing import Any

from option_quant_fund.data.sources.tq.config import TqConfig


class TqSdkNotInstalledError(ImportError):
    """Raised when connect() is called without the tqsdk package."""


def is_tqsdk_available() -> bool:
    """Report whether the optional tqsdk dependency is installed."""
    try:
        import tqsdk  # noqa: F401
    except ImportError:
        return False
    return True


class TqClient:
    """Offline-first TqSdk adapter entry point.

    Structure and env-var wiring only. Download code belongs in TASK-008.
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
        return cls(TqConfig.from_env(), auto_connect=auto_connect)

    @property
    def config(self) -> TqConfig:
        return self._config

    @property
    def is_connected(self) -> bool:
        return self._connected

    def connect(self) -> None:
        """Open a TqSdk session only when explicitly requested."""
        if self._connected:
            return

        if not is_tqsdk_available():
            raise TqSdkNotInstalledError(
                "tqsdk is not installed; install it locally before connect()"
            )

        from tqsdk import TqApi
        from tqsdk import TqAuth

        credentials = TqAuth(
            self._config.user,
            self._config.password,
        )
        self._api = TqApi(auth=credentials)
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
