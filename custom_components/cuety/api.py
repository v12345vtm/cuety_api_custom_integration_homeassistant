# Cuety-integratie, versie 5.2.0
"""Async client voor de Cuety/LPU-2 HTTP-API (https://api.visualproductions.nl/)."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import SPEED
from .virtueel import VirtueleQuety

_LOGGER = logging.getLogger(__name__)
_TIMEOUT = aiohttp.ClientTimeout(total=5)


class CueyError(HomeAssistantError):
    """De Quety is niet bereikbaar of gaf een foutmelding."""


def waarde_uit_antwoord(tekst: str) -> Any | None:
    """Haalt de waarde uit een antwoord zoals {"speed":0.20,"apicall":"succeeded"}.

    Geeft None als er geen waarde in zit, of als het antwoord geen JSON is.
    """
    try:
        data = json.loads(tekst)
    except (TypeError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    waarden = [waarde for sleutel, waarde in data.items() if sleutel != "apicall"]
    if len(waarden) != 1 or isinstance(waarden[0], dict):
        return None
    return waarden[0]


def _controleer(path: str, tekst: str) -> None:
    """Gooit een fout als de Quety apicall op iets anders dan 'succeeded' zet."""
    try:
        data = json.loads(tekst)
    except (TypeError, ValueError):
        return
    if isinstance(data, dict) and "apicall" in data and data["apicall"] != "succeeded":
        raise CueyError(f"Quety meldde een fout op '{path}': {tekst[:200]}")


def _pb(playback: int) -> str:
    """Playbacks worden aangesproken als pb01 t/m pb99."""
    return f"pb{playback:02d}"


def _delta(change: float) -> str:
    """Relatieve wijziging: ++0.05 is omhoog, -0.05 is omlaag."""
    return f"++{change:.2f}" if change >= 0 else f"{change:.2f}"


class CueyClient:
    """Praat met één Quety: via HTTP, of in de testmodus met de ingebouwde simulator."""

    def __init__(self, hass: HomeAssistant, host: str, port: int, demo: bool = False) -> None:
        self.host = host
        self.port = port
        self.demo = demo
        self.entry_id: str | None = None
        self.antwoord_signal: str | None = None
        self._hass = hass
        self._session = async_get_clientsession(hass)
        self._base = f"http://{host}:{port}/ajax"
        # Eén verzoek tegelijk: de Quety is een klein apparaat.
        self._lock = asyncio.Lock()
        # De testmodus heeft een eigen stand, zodat lichten en knoppen zich gedragen als bij een echte Quety.
        self._simulator = VirtueleQuety() if demo else None

    async def _http_get(self, url: str) -> tuple[int, str]:
        async with self._lock:
            try:
                async with self._session.get(url, timeout=_TIMEOUT) as resp:
                    return resp.status, (await resp.text(errors="replace")).strip()
            except (aiohttp.ClientError, TimeoutError) as err:
                raise CueyError(f"Quety {self.host}:{self.port} is niet bereikbaar") from err

    async def request(self, command: str, *, poll: bool = False) -> str:
        """Stuurt een commando. Met poll=True is het een opvraag van de stand, die niet in httpresponse komt."""
        path = command.strip().lstrip("/").removeprefix("ajax/")
        if self.demo:
            status, body = self._simulator.handle(f"/ajax/{path}")
            _LOGGER.debug("Testmodus: /ajax/%s -> %s %s", path, status, body)
        else:
            _LOGGER.debug("Cuety GET %s/%s", self._base, path)
            status, body = await self._http_get(f"{self._base}/{path}")
        if not poll and self.antwoord_signal:
            async_dispatcher_send(self._hass, self.antwoord_signal, f"/ajax/{path}", body)
        if status >= 400:
            raise CueyError(f"Quety antwoordde {status} op '{path}': {body[:200]}")
        _controleer(path, body)
        return body

    async def hello(self) -> str:
        return await self.request("hello")

    async def blackout(self, on: bool) -> str:
        return await self.request(f"blackout={int(on)}")

    async def get_blackout(self) -> bool | None:
        waarde = waarde_uit_antwoord(await self.request("blackout", poll=True))
        if waarde is None or isinstance(waarde, list):
            return None
        return bool(waarde)

    async def get_active_status(self) -> str:
        return await self.request("pbxx/ac")

    async def get_playback_active(self, playback: int) -> bool | None:
        waarde = waarde_uit_antwoord(await self.request(f"{_pb(playback)}/ac", poll=True))
        if waarde is None or isinstance(waarde, list):
            return None
        return bool(waarde)

    async def get_playback_intensity(self, playback: int) -> float | None:
        waarde = waarde_uit_antwoord(await self.request(f"{_pb(playback)}/int", poll=True))
        if waarde is None or isinstance(waarde, list):
            return None
        return float(waarde)

    async def get_active_cues(self) -> str:
        return await self.request("pbxx/cue")

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
