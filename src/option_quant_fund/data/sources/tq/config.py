"""TqSdk configuration loaded from environment variables only."""

from __future__ import annotations

import os
from dataclasses import dataclass

ENV_TQ_USER = "TQ_USER"
ENV_TQ_PASS = "TQ_PASS"


class TqConfigError(ValueError):
    """Raised when required TqSdk environment variables are missing or empty."""


@dataclass(frozen=True)
class TqEnvStatus:
    """Explicit readiness state for TqSdk credentials in the environment."""

    user_present: bool
    password_present: bool

    @property
    def complete(self) -> bool:
        return self.user_present and self.password_present

    @property
    def missing(self) -> tuple[str, ...]:
        missing: list[str] = []
        if not self.user_present:
            missing.append(ENV_TQ_USER)
        if not self.password_present:
            missing.append(ENV_TQ_PASS)
        return tuple(missing)


@dataclass(frozen=True)
class TqConfig:
    """TqSdk credentials resolved from environment variable names only."""

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
        status = check_env(user_var=user_var, pass_var=pass_var, environ=environ)
        if not status.complete:
            missing = ", ".join(status.missing)
            raise TqConfigError(
                f"Missing required TqSdk environment variable(s): {missing}"
            )

        env = os.environ if environ is None else environ
        return cls(user=env[user_var], password=env[pass_var])


def check_env(
    *,
    user_var: str = ENV_TQ_USER,
    pass_var: str = ENV_TQ_PASS,
    environ: dict[str, str] | None = None,
) -> TqEnvStatus:
    """Return whether TqSdk credential environment variables are present."""
    env = os.environ if environ is None else environ
    user = env.get(user_var)
    password = env.get(pass_var)
    return TqEnvStatus(
        user_present=bool(user),
        password_present=bool(password),
    )
