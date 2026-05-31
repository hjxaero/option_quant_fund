"""TqSdk client skeleton - no live connection by default."""

from __future__ import annotations

from typing import Any

from option_quant_fund.data.sources.tq.config import TqConfig


class TqSdkNotInstalledError(ImportError):
    """Raised when live connection is requested but tqsdk is not installed."""


def is_tqsdk_available() -> bool:
    """Return True when the optional tqsdk package is importable."""
    try:
        import tqsdk  # noqa: F401
    except ImportError:
        return False
    return True


class TqClient:
    """Skeleton adapter for Tianqin TqSdk.

    TASK-007 provides structure and env-var auth only. Downloader logic and
    live market-data calls belong in TASK-008+.
    """

    def __init__(self, config: TqConfig, *, auto_connect: bool = False) -> None:
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
        """Open a live TqSdk session. Requires optional tqsdk dependency."""
        if self._connected:
            return

        if not is_tqsdk_available():
            raise TqSdkNotInstalledError(
                "tqsdk is not installed; install it locally before calling connect()"
            )

        from tqsdk import TqApi, TqAuth

        self._api = TqApi(auth=TqAuth(self._config.user, self._config.password))
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
