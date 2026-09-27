"""Async account engine — the state machine that drives a batch run.

The engine owns concurrency, retries, and persistence. Handlers do the
work; the engine decides what happens when a handler succeeds or fails.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential_jitter

from forge.core.migrations import ensure_schema
from forge.core.state import AccountState, transition
from forge.handlers import HANDLERS, ForgeStepError, ForgeFatalError
from forge.models.account import Account
from forge.models.config import ForgeConfig
from forge.models.report import RunReport
from forge.services.tiktok import TikTokClient
from forge.utils.ids import new_account_id


@dataclass
class ForgeContext:
    """Shared run-scoped state passed to every handler."""

    config: ForgeConfig
    tiktok: TikTokClient
    semaphore: asyncio.Semaphore


class AccountEngine:
    """Drives accounts through the provisioning pipeline."""

    def __init__(self, config: ForgeConfig) -> None:
        self.config = config
        self._sem = asyncio.Semaphore(config.concurrency)
        self._client = TikTokClient(config)
        self._ctx = ForgeContext(config=config, tiktok=self._client, semaphore=self._sem)

    async def run_batch(self) -> RunReport:
        ensure_schema(self.config.state_db)
        accounts = [Account(id=new_account_id(), target=self.config.target_count) for _ in range(self.config.target_count)]
        logger.info("batch queued — {} accounts", len(accounts))
        results = await asyncio.gather(*(self._run_one(a) for a in accounts))
        return RunReport.from_accounts(results)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential_jitter(initial=2, max=8), reraise=True)
    async def _run_one(self, account: Account) -> Account:
        async with self._sem:
            for state in (
                AccountState.FINGERPRINTING,
                AccountState.PROXYING,
                AccountState.REGISTERING,
                AccountState.VERIFYING,
                AccountState.WARMING,
                AccountState.EXPORTED,
            ):
                transition(account, state)
                handler = HANDLERS[state.value]
                try:
                    await handler(account, self._ctx)
                except ForgeStepError as exc:
                    logger.warning("{} step {} retryable: {}", account.id, state.value, exc)
                    raise
                except ForgeFatalError as exc:
                    logger.error("{} step {} fatal: {}", account.id, state.value, exc)
                    account.fail(str(exc))
                    return account
            account.finish()
            return account

    async def aclose(self) -> None:
        await self._client.aclose()