"""Environment-based configuration for the TqSdk adapter skeleton."""

from __future__ import annotations

import os
from dataclasses import dataclass

ENV_TQ_USER = "TQ_USER"
ENV_TQ_PASS = "TQ_PASS"


class TqConfigError(ValueError):
    """Configuration is incomplete or invalid."""


@dataclass(frozen=True)
class TqEnvStatus:
    """Reports which credential environment variables are available."""

    user_present: bool
    password_present: bool

    @property
    def complete(self) -> bool:
        return self.user_present and self.password_present

    @property
    def missing(self) -> tuple[str, ...]:
        names: list[str] = []
        if not self.user_present:
            names.append(ENV_TQ_USER)
        if not self.password_present:
            names.append(ENV_TQ_PASS)
        return tuple(names)


@dataclass(frozen=True)
class TqConfig:
    """Resolved TqSdk credentials."""

    user: str
    password: str

    @classmethod
    def from_env(
        cls,
        *,
        user_var: str = ENV_TQ_USER,
        pass_var: str = ENV_TQ_PASS,
        environ: dict[str, str] | None = None,
    ) -> TqConfig:
        status = check_env(
            user_var=user_var,
            pass_var=pass_var,
            environ=environ,
        )
        if not status.complete:
            joined = ", ".join(status.missing)
            raise TqConfigError(
                "Missing required TqSdk environment variable(s): "
                + joined
            )

        source = os.environ if environ is None else environ
        return cls(
            user=source[user_var],
            password=source[pass_var],
        )


def check_env(
    *,
    user_var: str = ENV_TQ_USER,
    pass_var: str = ENV_TQ_PASS,
    environ: dict[str, str] | None = None,
) -> TqEnvStatus:
    """Inspect credential variables without connecting to TqSdk."""
    source = os.environ if environ is None else environ
    username = source.get(user_var)
    password = source.get(pass_var)
    return TqEnvStatus(
        user_present=bool(username),
        password_present=bool(password),
    )
