"""Verification handler — solves the email/SMS challenge step."""

from __future__ import annotations

from loguru import logger

from forge.handlers import ForgeStepError, register_handler
from forge.models.account import Account
from forge.services.mail import MailService


@register_handler("verifying")
async def handle(account: Account, ctx) -> None:
    """Drive email verification for a freshly-registered account."""
    if account.session is None:
        raise ForgeStepError("no session to verify")
    mail = MailService(ctx.config)
    inbox = await mail.provision(prefix=account.id[:8])
    try:
        code = await mail.await_code(inbox, timeout=180)
    except TimeoutError as exc:
        raise ForgeStepError("verification code timed out") from exc
    await ctx.tiktok.submit_code(account.session, code)
    await mail.release(inbox)
    logger.debug("{} verified via {}", account.id, inbox.address)