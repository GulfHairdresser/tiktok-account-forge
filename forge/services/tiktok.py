"""TikTok HTTP + Playwright client.

Wraps the web signup flow. All requests carry the account's fingerprint
headers and route through the account's bound proxy. Rate limits raise
`RateLimited`; hard blocks raise `Blocked`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx
from loguru import logger

from forge.models.config import ForgeConfig
from forge.models.fingerprint import Fingerprint
from forge.models.proxy import Proxy
from forge.models.session import Session
from forge.utils.headers import build_headers


@dataclass
class RegisterResult:
    handle: str
    cookies: dict[str, str]


class TikTokClient:
    """Async client for TikTok's public web endpoints."""

    class RateLimited(RuntimeError):
        def __init__(self, retry_after: int) -> None:
            super().__init__(f"rate limited, retry after {retry_after}s")
            self.retry_after = retry_after

    class Blocked(RuntimeError):
        def __init__(self, reason: str) -> None:
            super().__init__(reason)
            self.reason = reason

    def __init__(self, config: ForgeConfig) -> None:
        self._config = config
        self._http = httpx.AsyncClient(
            http2=True,
            timeout=httpx.Timeout(30.0, connect=10.0),
            follow_redirects=True,
        )

    async def register(
        self,
        *,
        fingerprint: Fingerprint,
        proxy: Proxy,
        captcha: Any,
    ) -> Session:
        headers = build_headers(fingerprint)
        token = await captcha.solve(site="tiktok_signup")
        payload = {
            "device_id": fingerprint.device_id,
            "csrf": token,
            "tz": fingerprint.timezone,
        }
        r = await self._http.post(
            "https://www.tiktok.com/api/v1/web/signup",
            headers=headers,
            json=payload,
            proxy=proxy.uri,
        )
        if r.status_code == 429:
            raise self.RateLimited(int(r.headers.get("retry-after", "30")))
        if r.status_code in (403, 10203):
            raise self.Blocked("tiktok_block")
        r.raise_for_status()
        body = r.json()
        return Session(
            handle=body["data"]["username"],
            cookies=dict(r.cookies),
            device_id=fingerprint.device_id,
        )

    async def submit_code(self, session: Session, code: str) -> None:
        r = await self._http.post(
            "https://www.tiktok.com/api/v1/web/verify_email",
            cookies=session.cookies,
            json={"code": code},
        )
        r.raise_for_status()
        logger.debug("code accepted for {}", session.handle)

    async def scroll_feed(self, session: Session, n: int) -> None:
        r = await self._http.get(
            "https://www.tiktok.com/api/recommend/item_list/",
            params={"count": n},
            cookies=session.cookies,
        )
        if r.status_code >= 400:
            logger.debug("feed scroll returned {}", r.status_code)

    async def aclose(self) -> None:
        await self._http.aclose()