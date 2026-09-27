"""Registration handler — drives the signup flow via Playwright."""

from __future__ import annotations

from loguru import logger

from forge.handlers import ForgeStepError, register_handler
from forge.models.account import Account
from forge.services.captcha import CaptchaService
from forge.services.tiktok import TikTokClient


@register_handler("registering")
async def handle(account: Account, ctx) -> None:
    """Register a TikTok account for `account` using its fingerprint + proxy."""
    if account.fingerprint is None or account.proxy is None:
        raise ForgeStepError("registration requires fingerprint and proxy")
    client: TikTokClient = ctx.tiktok
    captcha = CaptchaService(ctx.config)
    try:
        session = await client.register(
            fingerprint=account.fingerprint,
            proxy=account.proxy,
            captcha=captcha,
        )
    except TikTokClient.RateLimited as exc:
        raise ForgeStepError(f"rate limited: retry-after={exc.retry_after}s") from exc
    except TikTokClient.Blocked as exc:
        account.fail(f"blocked: {exc.reason}")
        logger.warning("{} blocked during registration: {}", account.id, exc.reason)
        return
    account.session = session
    account.handle = session.handle
    logger.info("{} registered handle={}", account.id, session.handle)