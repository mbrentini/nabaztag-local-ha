"""Async client for the local nabaztag-violet control API."""

from __future__ import annotations

from typing import Any

import aiohttp
from yarl import URL

TIMEOUT = aiohttp.ClientTimeout(total=20)


class NabaztagApiError(Exception):
    """An error returned by the Nabaztag server."""


class NabaztagClient:
    """Client for the documented nabaztag-violet HTTP control API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        base_url: str,
        api_token: str | None = None,
        mac: str | None = None,
    ) -> None:
        self._session = session
        self._base = URL(base_url.rstrip("/") + "/")
        self._api_token = api_token
        self._mac = mac

    @property
    def base_url(self) -> str:
        return str(self._base).rstrip("/")

    @property
    def mac(self) -> str | None:
        return self._mac

    def _headers(self) -> dict[str, str]:
        return {"X-API-Token": self._api_token} if self._api_token else {}

    async def request(
        self,
        path: str,
        *,
        params: dict[str, Any] | list[tuple[str, Any]] | None = None,
        method: str = "GET",
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = self._base.join(URL(path.lstrip("/")))
        if self._mac and path.startswith("/api/") and not path.startswith("/api/adoption"):
            if isinstance(params, dict):
                params = {**params, "mac": self._mac}
            else:
                params = list(params or []) + [("mac", self._mac)]
        try:
            async with self._session.request(
                method,
                url,
                params=params,
                json=json_body,
                headers=self._headers(),
                timeout=TIMEOUT,
            ) as response:
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
        except NabaztagApiError:
            raise
        except (aiohttp.ClientError, TimeoutError) as err:
            raise NabaztagApiError(str(err)) from err

    async def download(self, path: str, *, params: dict[str, Any] | None = None) -> bytes:
        url = self._base.join(URL(path.lstrip("/")))
        if self._mac and path.startswith("/api/"):
            params = {**(params or {}), "mac": self._mac}
        try:
            async with self._session.get(
                url, params=params, headers=self._headers(), timeout=TIMEOUT
            ) as response:
                if response.status >= 400:
                    try:
                        data = await response.json(content_type=None)
                        detail = data.get("error", f"HTTP {response.status}")
                    except (ValueError, aiohttp.ContentTypeError):
                        detail = f"HTTP {response.status}"
                    raise NabaztagApiError(str(detail))
                return await response.read()
        except NabaztagApiError:
            raise
        except (aiohttp.ClientError, TimeoutError) as err:
            raise NabaztagApiError(str(err)) from err

    async def status(self) -> dict[str, Any]:
        """Read server status from its root endpoint."""
        return await self.request("")

    async def say(self, text: str, *, voice: str = "fr", speed: int = 160, pitch: int = 50, wait: bool = False) -> dict[str, Any]:
        return await self.request("/api/say", params={"text": text, "voice": voice, "speed": speed, "pitch": pitch, "wait": int(wait)})

    async def play(self, url: str, *, wait: bool = False) -> dict[str, Any]:
        return await self.request("/api/play", params={"url": url, "wait": int(wait)})

    async def jingle(self, name: str, *, wait: bool = False) -> dict[str, Any]:
        return await self.request("/api/jingle", params={"name": name, "wait": int(wait)})

    async def ears(self, left: int, right: int, direction: int = 0) -> dict[str, Any]:
        return await self.request("/api/ears", params={"left": left, "right": right, "dir": direction})

    async def led(self, led: str, rgb: tuple[int, int, int]) -> dict[str, Any]:
        return await self.request("/api/led", params={"led": led, "r": rgb[0], "g": rgb[1], "b": rgb[2]})

    async def weather(self, value: str) -> dict[str, Any]:
        return await self.request("/api/weather", params={"v": value})

    async def nose(self, value: int) -> dict[str, Any]:
        return await self.request("/api/nose", params={"v": value})

    async def ear_wiggle(self, left: int = 1, right: int = 1) -> dict[str, Any]:
        return await self.request("/api/earwiggle", params={"left": left, "right": right})

    async def bottom_led(self, value: int) -> dict[str, Any]:
        return await self.request("/api/bottomled", params={"v": value})

    async def sleep(self, asleep: bool) -> dict[str, Any]:
        return await self.request("/api/sleep", params={"on": int(asleep)})

    async def volume(self, level: int) -> dict[str, Any]:
        return await self.request("/api/volume", params={"level": level})

    async def mic(self, enabled: bool) -> dict[str, Any]:
        return await self.request("/api/mic", params={"on": int(enabled)})

    async def state(self) -> dict[str, Any]:
        return await self.request("/api/state")

    async def personality(self) -> dict[str, Any]:
        return await self.request("/api/personality")

    async def choreography(self, spec: str) -> dict[str, Any]:
        return await self.request("/api/choreography", params={"spec": spec})

    async def program(self, text: str) -> dict[str, Any]:
        return await self.request("/api/program", params={"text": text})

    async def ambient(self, services: list[int], values: list[int]) -> dict[str, Any]:
        params = [("svc", service) for service in services]
        params.extend(("val", value) for value in values)
        return await self.request("/api/ambient", params=params)

    async def raw(self, packet_b64: str) -> dict[str, Any]:
        return await self.request("/api/raw", params={"b64": packet_b64})

    async def adoption(self) -> dict[str, Any]:
        return await self.request("/api/adoption")

    async def adoption_action(self, action: str, mac: str, fingerprint: str | None = None) -> dict[str, Any]:
        return await self.request(
            f"/api/adoption/{action}",
            method="POST",
            json_body={"mac": mac, **({"fingerprint": fingerprint} if fingerprint else {})},
        )

    async def stage_ota(self, path: str, name: str, trigger: bool, mac: str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {"path": path, "name": name, "trigger": int(trigger)}
        if mac:
            params["mac"] = mac
        return await self.request("/api/ota", params=params, method="POST")

    async def last_recording(self, audio_format: str = "pcm") -> bytes:
        return await self.download("/api/lastrecording", params={"format": audio_format})
