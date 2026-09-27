"""Fingerprint-consistent HTTP header builder."""

from __future__ import annotations

from forge.models.fingerprint import Fingerprint


def headers_for(fp: Fingerprint) -> dict[str, str]:
    """Return request headers matching the fingerprint's identity."""
    return {
        "user-agent": fp.user_agent,
        "accept-language": fp.locale,
        "x-tt-tz": fp.timezone,
        "x-tt-device-id": fp.device_id,
        "x-tt-screen": f"{fp.screen_width}x{fp.screen_height}",
    }