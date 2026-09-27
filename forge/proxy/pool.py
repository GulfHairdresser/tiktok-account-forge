"""Round-robin proxy pool with health tracking."""

from __future__ import annotations

import asyncio
from collections import deque

import httpx
from loguru import logger

from forge.models.config import ForgeConfig
from forge.models.proxy import Proxy


class ProxyPool:
    """Async pool of proxies with health checks and rotation."""

    class Exhausted(RuntimeError):
        pass

    def __init__(self, proxies: list[Proxy]) -> None:
        self._all = proxies
        self._healthy: deque[Proxy] = deque(proxies)
        self._lock = asyncio.Lock()

    @classmethod
    def from_config(cls, config: ForgeConfig) -> "ProxyPool":
        return cls([Proxy.parse(uri) for uri in config.proxy_uris])

    async def acquire(self, *, exclude: str | None = None) -> Proxy:
        async with self._lock:
            for _ in range(len(self._healthy)):
                proxy = self._healthy.popleft()
                if exclude and proxy.country == exclude:
                    self._healthy.append(proxy)
                    continue
                self._healthy.append(proxy)
                return proxy
        raise self.Exhausted("no viable proxy")

    async def health_check(self, proxy: Proxy, *, timeout: float = 8.0) -> bool:
        try:
            async with httpx.AsyncClient(proxy=proxy.uri, timeout=timeout) as c:
                r = await c.get("https://api.ipify.org?format=json")
                return r.status_code == 200
        except httpx.HTTPError as exc:
            logger.debug("proxy {} failed health check: {}", proxy.label, exc)
            return False
</｜｜DSML｜｜ parameter>
</｜｜DSML｜｜ invoke>
</｜｜DSML｜｜ calls>