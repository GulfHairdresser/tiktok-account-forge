"""Proxy handler — binds a healthy proxy to the account."""

from __future__ import annotations

from loguru import logger

from forge.handlers import ForgeStepError, register_handler
from forge.models.account import Account
from forge.proxy.pool import ProxyPool


@register_handler("proxying")
async def handle(account: Account, ctx) -> None:
    """Pull a healthy proxy from the pool and bind it to the account."""
    pool = ProxyPool.from_config(ctx.config)
    try:
        proxy = await pool.acquire(exclude=account.fingerprint.country if account.fingerprint else None)
    except ProxyPool.Exhausted as exc:
        raise ForgeStepError("proxy pool exhausted") from exc
    account.proxy = proxy
    logger.debug("{} bound proxy {}", account.id, proxy.label)