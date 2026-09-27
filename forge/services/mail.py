"""Disposable inbox provisioning for verification codes."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

import httpx
from loguru import logger

from forge.models.config import ForgeConfig


@dataclass
class Inbox:
    address: str
    token: str


class MailService:
    """Thin wrapper over a mail API provider."""

    def __init__(self, config: ForgeConfig) -> None:
        self._config = config
        self._http = httpx.AsyncClient(timeout=20.0)

    async def provision(self, *, prefix: str) -> Inbox:
        r = await self._http.post(
            f"{self._config.mail_api_base}/inboxes",
            headers={"Authorization": f"Bearer {self._config.mail_api_key}"},
            json={"prefix": prefix, "domain": self._config.mail_domain},
        )
        r.raise_for_status()
        body = r.json()
        return Inbox(address=body["address"], token=body["token"])

    async def await_code(self, inbox: Inbox, *, timeout: int) -> str:
        deadline = asyncio.get_event_loop().time() + timeout
        while asyncio.get_event_loop().time() < deadline:
            r = await self._http.get(
                f"{self._config.mail_api_base}/inboxes/{inbox.token}/messages",
                headers={"Authorization": f"Bearer {self._config.mail_api_key}"},
            )
            if r.status_code == 200:
                for msg in r.json().get("messages", []):
                    if code := _extract_code(msg.get("body", "")):
                        return code
            await asyncio.sleep(3.0)
        raise TimeoutError("no verification code arrived")

    async def release(self, inbox: Inbox) -> None:
        await self._http.delete(
            f"{self._config.mail_api_base}/inboxes/{inbox.token}",
            headers={"Authorization": f"Bearer {self._config.mail_api_key}"},
        )
        logger.debug("released inbox {}", inbox.address)


def _extract_code(body: str) -> str | None:
    import re

    if m := re.search(r"\b(\d{6})\b", body):
        return m.group(1)
    return None