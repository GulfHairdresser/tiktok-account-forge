"""Account state machine — legal transitions and guard rails."""

from __future__ import annotations

from enum import Enum

from forge.models.account import Account


class AccountState(str, Enum):
    QUEUED = "queued"
    FINGERPRINTING = "fingerprinting"
    PROXYING = "proxying"
    REGISTERING = "registering"
    VERIFYING = "verifying"
    WARMING = "warming"
    EXPORTED = "exported"
    FAILED = "failed"


_LEGAL: dict[AccountState, set[AccountState]] = {
    AccountState.QUEUED: {AccountState.FINGERPRINTING, AccountState.FAILED},
    AccountState.FINGERPRINTING: {AccountState.PROXYING, AccountState.FAILED},
    AccountState.PROXYING: {AccountState.REGISTERING, AccountState.FAILED},
    AccountState.REGISTERING: {AccountState.VERIFYING, AccountState.FAILED},
    AccountState.VERIFYING: {AccountState.WARMING, AccountState.FAILED},
    AccountState.WARMING: {AccountState.EXPORTED, AccountState.FAILED},
    AccountState.EXPORTED: set(),
    AccountState.FAILED: set(),
}


def transition(account: Account, to: AccountState) -> None:
    """Move `account` to `to`, raising if the transition is illegal."""
    current = AccountState(account.state)
    if to not in _LEGAL[current]:
        raise ValueError(f"illegal transition {current.value} -> {to.value}")
    account.state = to.value