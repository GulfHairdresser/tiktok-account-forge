"""Warming handler — post-registration activity to age the session."""

from __future__ import annotations

import asyncio
import random

from loguru import logger

from forge.handlers import ForgeStepError, register_handler
from forge.models.account import Account


@register_handler("warming")
async def handle(account: Account, ctx) -> None:
    """Simulate light human activity so the session isn't flagged cold."""
    if account.session is None:
        raise ForgeStepError("cannot warm a sessionless account")
    actions = random.randint(3, 7)
    for _ in range(actions):
        await asyncio.sleep(random.uniform(4.0, 12.0))
        try:
            await ctx.tiktok.scroll_feed(account.session, n=random.randint(2, 5))
        except Exception as exc:  # noqa: BLE001 — warming is best-effort
            logger.debug("{} warming hiccup: {}", account.id, exc)
    logger.debug("{} warmed with {} actions", account.id, actions)