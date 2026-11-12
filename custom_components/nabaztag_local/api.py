"""Async client for the local nabaztag-violet control API."""

from __future__ import annotations

from typing import Any

import aiohttp
from yarl import URL

TIMEOUT = aiohttp.ClientTimeout(total=10)


class NabaztagApiError(Exception):
    """An error returned by the Nabaztag server."""


class NabaztagClient:
    """Small client for the documented /api endpoints."""

    def __init__(self, session: aiohttp.ClientSession, base_url: str) -> None:
        self._session = session
        self._base = URL(base_url.rstrip("/") + "/")

    @property
    def base_url(self) -> str:
        return str(self._base).rstrip("/")

    async def request(
        self, path: str, *, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        url = self._base.join(URL(path.lstrip("/")))
        try:
            async with self._session.get(url, params=params, timeout=TIMEOUT) as response:
                try:
                    data = await response.json(content_type=None)
                except (ValueError, aiohttp.ContentTypeError):
                    data = {}
                if response.status >= 400:
                    detail = data.get("error", f"HTTP {response.status}") if isinstance(data, dict) else f"HTTP {response.status}"
                    raise NabaztagApiError(str(detail))
                if not isinstance(data, dict):
                    raise NabaztagApiError("Réponse inattendue du serveur")
                return data
        except (aiohttp.ClientError, TimeoutError) as err:
            raise NabaztagApiError(str(err)) from err

    async def status(self) -> dict[str, Any]:
        return await self.request("/api/status")

    async def say(self, text: str, *, voice: str = "fr", speed: int = 160, pitch: int = 50) -> dict[str, Any]:
        return await self.request("/api/say", params={"text": text, "voice": voice, "speed": speed, "pitch": pitch})

    async def jingle(self, name: str) -> dict[str, Any]:
        return await self.request("/api/jingle", params={"name": name})

    async def ears(self, left: int, right: int) -> dict[str, Any]:
        return await self.request("/api/ears", params={"left": left, "right": right})

    async def led(self, led: str, rgb: tuple[int, int, int]) -> dict[str, Any]:
        return await self.request("/api/led", params={"led": led, "r": rgb[0], "g": rgb[1], "b": rgb[2]})

    async def weather(self, value: str) -> dict[str, Any]:
        return await self.request("/api/weather", params={"v": value})

    async def nose(self, value: int) -> dict[str, Any]:
        return await self.request("/api/nose", params={"v": value})

    async def sleep(self, asleep: bool) -> dict[str, Any]:
        return await self.request("/api/sleep", params={"on": int(asleep)})

    async def volume(self, level: int) -> dict[str, Any]:
        return await self.request("/api/volume", params={"level": level})
