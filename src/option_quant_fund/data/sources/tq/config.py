"""Credential helpers for the TqSdk adapter."""

from __future__ import annotations

import os
from dataclasses import dataclass

ENV_TQ_USER = "TQ_USER"
ENV_TQ_PASS = "TQ_PASS"


class TqConfigError(ValueError):
    """Environment variables required by TqSdk are unavailable."""


@dataclass(frozen=True)
class TqEnvStatus:
    """Tracks whether credential variables exist."""

    user_present: bool
    password_present: bool

    @property
    def complete(self) -> bool:
        if not self.user_present:
            return False
        if not self.password_present:
            return False
        return True

    @property
    def missing(self) -> tuple[str, ...]:
        result: list[str] = []
        if not self.user_present:
            result.append(ENV_TQ_USER)
        if not self.password_present:
            result.append(ENV_TQ_PASS)
        return tuple(result)


@dataclass(frozen=True)
class TqConfig:
    """Username and password read from the process environment."""

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
            detail = ", ".join(status.missing)
            raise TqConfigError(
                "Missing required TqSdk environment variable(s): "
                + detail
            )

        values = os.environ if environ is None else environ
        user_value = values[user_var]
        pass_value = values[pass_var]
        return cls(user=user_value, password=pass_value)


def check_env(
    *,
    user_var: str = ENV_TQ_USER,
    pass_var: str = ENV_TQ_PASS,
    environ: dict[str, str] | None = None,
) -> TqEnvStatus:
    """Inspect credential variables without network access."""
    values = os.environ if environ is None else environ
    user_value = values.get(user_var)
    pass_value = values.get(pass_var)
    return TqEnvStatus(
        user_present=bool(user_value),
        password_present=bool(pass_value),
    )
