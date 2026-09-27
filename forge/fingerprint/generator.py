"""Deterministic fingerprint generator seeded by account id.

Same seed → same fingerprint. That keeps retries idempotent: a retried
account gets the same device it had on its first attempt, so TikTok
doesn't see the identity change mid-run.
"""

from __future__ import annotations

import hashlib
import random

from fake_useragent import UserAgent

from forge.models.fingerprint import Fingerprint

_UA = UserAgent(browsers=["chrome", "edge"])
_TIMEZONES = ["America/New_York", "Europe/Berlin", "Asia/Tokyo", "America/Sao_Paulo"]
_LOCALES = ["en-US", "en-GB", "de-DE", "ja-JP", "pt-BR"]
_SCREENS = [(1920, 1080), (2560, 1440), (1536, 864), (1366, 768)]


class FingerprintGenerator:
    """Build a coherent fingerprint from a stable seed."""

    def __init__(self, seed: str) -> None:
        digest = hashlib.sha256(seed.encode()).digest()
        self._rng = random.Random(int.from_bytes(digest[:8], "big"))

    def build(self) -> Fingerprint:
        timezone = self._rng.choice(_TIMEZONES)
        locale = self._rng.choice(_LOCALES)
        width, height = self._rng.choice(_SCREENS)
        return Fingerprint(
            fingerprint_id=self._rng.getrandbits(64).to_bytes(8, "big").hex(),
            device_id=self._rng.getrandbits(64).to_bytes(8, "big").hex(),
            user_agent=_UA.random,
            timezone=timezone,
            locale=locale,
            screen_width=width,
            screen_height=height,
            country=timezone.split("/")[0],
            webgl_vendor=self._rng.choice(["Google Inc.", "Intel Inc.", "Apple Inc."]),
        )