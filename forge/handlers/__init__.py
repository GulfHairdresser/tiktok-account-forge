"""Feature handlers — one per pipeline step, registered by name."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from forge.core.engine import ForgeContext
    from forge.models.account import Account

Handler = Callable[["Account", "ForgeContext"], Awaitable[None]]

HANDLERS: dict[str, Handler] = {}


class ForgeStepError(RuntimeError):
    """Retryable step failure — the engine will back off and retry."""


class ForgeFatalError(RuntimeError):
    """Terminal step failure — the account is parked in FAILED."""


def register_handler(name: str) -> Callable[[Handler], Handler]:
    """Register a handler under a pipeline state name."""

    def _wrap(fn: Handler) -> Handler:
        HANDLERS[name] = fn
        return fn

    return _wrap


from forge.handlers import (  # noqa: E402,F401  (registers on import)
    fingerprinting,
    proxying,
    registering,
    verifying,
    warming,
)

__all__ = ["HANDLERS", "ForgeStepError", "ForgeFatalError", "register_handler"]