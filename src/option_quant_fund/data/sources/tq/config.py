"""Load TqSdk credentials from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass

ENV_TQ_USER = "TQ_USER"
ENV_TQ_PASS = "TQ_PASS"


class TqConfigError(ValueError):
    """Raised when TqSdk credentials are missing from the environment."""


@dataclass(frozen=True)
class TqEnvStatus:
    """Summarize credential variable presence."""

    user_present: bool
    password_present: bool

    @property
    def complete(self) -> bool:
        return self.user_present and self.password_present

    @property
    def missing(self) -> tuple[str, ...]:
        absent: list[str] = []
        if not self.user_present:
            absent.append(ENV_TQ_USER)
        if not self.password_present:
            absent.append(ENV_TQ_PASS)
        return tuple(absent)


@dataclass(frozen=True)
class TqConfig:
    """Credential pair for TqSdk authentication."""

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
            names = ", ".join(status.missing)
            raise TqConfigError(
                "Missing required TqSdk environment variable(s): "
                + names
            )

        mapping = os.environ if environ is None else environ
        return cls(
            user=mapping[user_var],
            password=mapping[pass_var],
        )


def check_env(
    *,
    user_var: str = ENV_TQ_USER,
    pass_var: str = ENV_TQ_PASS,
    environ: dict[str, str] | None = None,
) -> TqEnvStatus:
    """Check credential variables without opening a TqSdk session."""
    mapping = os.environ if environ is None else environ
    username = mapping.get(user_var)
    secret = mapping.get(pass_var)
    return TqEnvStatus(
        user_present=bool(username),
        password_present=bool(secret),
    )
