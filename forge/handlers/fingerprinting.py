"""Fingerprinting handler — assigns a device + browser fingerprint."""

from __future__ import annotations

from loguru import logger

from forge.fingerprint.generator import FingerprintGenerator
from forge.handlers import ForgeStepError, register_handler
from forge.models.account import Account


@register_handler("fingerprinting")
async def handle(account: Account, ctx) -> None:
    """Generate and attach a fresh device fingerprint to the account."""
    gen = FingerprintGenerator(seed=account.id)
    try:
        fp = gen.build()
    except Exception as exc:  # noqa: BLE001 — generator is third-party-ish
        raise ForgeStepError(f"fingerprint generation failed: {exc}") from exc
    account.fingerprint = fp
    logger.debug("{} assigned fingerprint {}", account.id, fp.fingerprint_id)