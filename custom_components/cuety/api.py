"""Async client voor de Cuety/LPU-2 HTTP-API (https://api.visualproductions.nl/)."""
from __future__ import annotations

import asyncio
import logging

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import SPEED

_LOGGER = logging.getLogger(__name__)
_TIMEOUT = aiohttp.ClientTimeout(total=5)


class CueyError(HomeAssistantError):
    """De Quety is niet bereikbaar of gaf een foutmelding."""


def _pb(playback: int) -> str:
    """Playbacks worden aangesproken als pb01 t/m pb99."""
    return f"pb{playback:02d}"


def _delta(change: float) -> str:
    """Relatieve wijziging: ++0.05 is omhoog, -0.05 is omlaag."""
    return f"++{change:.2f}" if change >= 0 else f"{change:.2f}"


class CueyClient:
    """Praat met één Quety. Elke methode geeft de tekstrespons terug."""

    def __init__(self, hass: HomeAssistant, host: str, port: int, demo: bool = False) -> None:
        self.host = host
        self.port = port
        self.demo = demo
        self._session = async_get_clientsession(hass)
        self._base = f"http://{host}:{port}/ajax"

    async def request(self, command: str) -> str:
        path = command.strip().lstrip("/").removeprefix("ajax/")
        url = f"{self._base}/{path}"
        if self.demo:
            _LOGGER.warning("Testmodus, niets verstuurd. Zou gaan naar GET %s", url)
            return "demo"
        _LOGGER.debug("Cuety GET %s", url)
        try:
            async with self._session.get(url, timeout=_TIMEOUT) as resp:
                body = (await resp.text(errors="replace")).strip()
        except (aiohttp.ClientError, TimeoutError) as err:
            raise CueyError(f"Quety {self.host}:{self.port} is niet bereikbaar") from err
        if resp.status >= 400:
            raise CueyError(f"Quety antwoordde {resp.status} op '{path}': {body[:200]}")
        return body

    async def hello(self) -> str:
        return await self.request("hello")

    async def blackout(self, on: bool) -> str:
        return await self.request(f"blackout={int(on)}")

    async def get_active_cues(self) -> str:
        return await self.request("pbxx/cue")

    async def get_active_status(self) -> str:
        return await self.request("pbxx/ac")

    async def release_all(self) -> str:
        return await self.request("pbxx/rel")

    async def go(self, playback: int) -> str:
        return await self.request(f"{_pb(playback)}/go+")

    async def go_back(self, playback: int) -> str:
        return await self.request(f"{_pb(playback)}/go-")

    async def release(self, playback: int) -> str:
        return await self.request(f"{_pb(playback)}/rel")

    async def jump(self, playback: int, cue: int) -> str:
        return await self.request(f"{_pb(playback)}/jmp={cue}")

    async def flash(self, playback: int, on: bool) -> str:
        return await self.request(f"{_pb(playback)}/fla={int(on)}")

    async def press_button(self, playback: int, duration: float) -> None:
        """Knop nabootsen: kort = go+, lang = release. Eerst btn=1, daarna btn=0."""
        await self.request(f"{_pb(playback)}/btn=1")
        try:
            await asyncio.sleep(duration)
        finally:
            await self.request(f"{_pb(playback)}/btn=0")

    async def set_intensity(self, playback: int, value: float) -> str:
        return await self.request(f"{_pb(playback)}/int={value:.2f}")

    async def change_intensity(self, playback: int, delta: float) -> str:
        return await self.request(f"{_pb(playback)}/int={_delta(delta)}")

    async def get_intensity(self, playback: int) -> str:
        return await self.request(f"{_pb(playback)}/int")

    async def set_speed(self, playback: int, value: float) -> str:
        return await self.request(f"{_pb(playback)}/{SPEED}={value:.2f}")

    async def change_speed(self, playback: int, delta: float) -> str:
        return await self.request(f"{_pb(playback)}/{SPEED}={_delta(delta)}")

    async def get_speed(self, playback: int) -> str:
        return await self.request(f"{_pb(playback)}/{SPEED}")

    async def set_all_intensity(self, value: float) -> str:
        return await self.request(f"pbxx/int={value:.2f}")

    async def get_all_intensity(self) -> str:
        return await self.request("pbxx/int")

    async def set_all_speed(self, value: float) -> str:
        return await self.request(f"pbxx/{SPEED}={value:.2f}")

    async def get_all_speed(self) -> str:
        return await self.request(f"pbxx/{SPEED}")