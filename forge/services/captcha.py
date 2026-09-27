"""Captcha solver service — talks to a third-party solver API."""

from __future__ import annotations

import asyncio

import httpx

from forge.models.config import ForgeConfig


class CaptchaService:
    """Submit a captcha task and poll for its token."""

    def __init__(self, config: ForgeConfig) -> None:
        self._config = config
        self._http = httpx.AsyncClient(timeout=30.0)

    async def solve(self, *, site: str) -> str:
        if not self._config.captcha_api_key:
            raise RuntimeError("no captcha_api_key configured")
        r = await self._http.post(
            f"{self._config.captcha_api_base}/createTask",
            json={"clientKey": self._config.captcha_api_key, "task": {"type": "TikTok", "site": site}},
        )
        r.raise_for_status()
        task_id = r.json()["taskId"]
        for _ in range(40):
            await asyncio.sleep(2.0)
            rr = await self._http.post(
                f"{self._config.captcha_api_base}/getTaskResult",
                json={"clientKey": self._config.captcha_api_key, "taskId": task_id},
            )
            body = rr.json()
            if body.get("status") == "ready":
                return body["solution"]["token"]
        raise TimeoutError(f"captcha task {task_id} did not resolve")