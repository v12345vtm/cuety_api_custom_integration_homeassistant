"""Cuety (LPU-2): playbacks, intensiteit en blackout aansturen via de lokale HTTP-API."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .api import CueyClient, CueyError
from .const import CONF_DEMO, CONF_HOST, CONF_PORT, DOMAIN

PLATFORMS = [Platform.SWITCH, Platform.NUMBER, Platform.BUTTON]

CueyConfigEntry = ConfigEntry[CueyClient]
Call = Callable[[CueyClient, dict[str, Any]], Awaitable[Any]]

# Schema-onderdelen
QUETY = {vol.Optional("quety"): cv.string}
PB = {vol.Required("playback"): vol.All(vol.Coerce(int), vol.Range(min=1, max=99))}
UNIT = vol.All(vol.Coerce(float), vol.Range(min=0, max=1))
BIPOLAR = vol.All(vol.Coerce(float), vol.Range(min=-1, max=1))
CUE = vol.All(vol.Coerce(int), vol.Range(min=1, max=48))
DURATION = vol.All(vol.Coerce(float), vol.Range(min=0.05, max=5))

# service: (extra velden, aanroep op de client, geeft het antwoord terug?)
SERVICES: dict[str, tuple[dict, Call, bool]] = {
    "go_plus": (PB, lambda c, d: c.go(d["playback"]), False),
    "go_back": (PB, lambda c, d: c.go_back(d["playback"]), False),
    "release": (PB, lambda c, d: c.release(d["playback"]), False),
    "release_all": ({}, lambda c, d: c.release_all(), False),
    "jump": ({**PB, vol.Required("cue"): CUE}, lambda c, d: c.jump(d["playback"], d["cue"]), False),
    "flash": ({**PB, vol.Required("on"): cv.boolean}, lambda c, d: c.flash(d["playback"], d["on"]), False),
    "press_button": (
        {**PB, vol.Optional("duration", default=0.1): DURATION},
        lambda c, d: c.press_button(d["playback"], d["duration"]),
        False,
    ),
    "set_intensity": (
        {**PB, vol.Required("value"): UNIT},
        lambda c, d: c.set_intensity(d["playback"], d["value"]),
        False,
    ),
    "change_intensity": (
        {**PB, vol.Required("delta"): BIPOLAR},
        lambda c, d: c.change_intensity(d["playback"], d["delta"]),
        False,
    ),
    "get_intensity": (PB, lambda c, d: c.get_intensity(d["playback"]), True),
    "set_speed": (
        {**PB, vol.Required("value"): BIPOLAR},
        lambda c, d: c.set_speed(d["playback"], d["value"]),
        False,
    ),
    "change_speed": (
        {**PB, vol.Required("delta"): BIPOLAR},
        lambda c, d: c.change_speed(d["playback"], d["delta"]),
        False,
    ),
    "get_speed": (PB, lambda c, d: c.get_speed(d["playback"]), True),
    "set_all_intensity": ({vol.Required("value"): UNIT}, lambda c, d: c.set_all_intensity(d["value"]), False),
    "get_all_intensity": ({}, lambda c, d: c.get_all_intensity(), True),
    "set_all_speed": ({vol.Required("value"): UNIT}, lambda c, d: c.set_all_speed(d["value"]), False),
    "get_all_speed": ({}, lambda c, d: c.get_all_speed(), True),
    "get_active_cues": ({}, lambda c, d: c.get_active_cues(), True),
    "get_active_status": ({}, lambda c, d: c.get_active_status(), True),
    "blackout": ({vol.Required("on"): cv.boolean}, lambda c, d: c.blackout(d["on"]), False),
    "hello": ({}, lambda c, d: c.hello(), True),
    "raw": ({vol.Required("command"): cv.string}, lambda c, d: c.request(d["command"]), True),
}


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Registreer de services één keer, ook als er meerdere Quety's zijn."""
    for name, (fields, func, returns) in SERVICES.items():
        hass.services.async_register(
            DOMAIN,
            name,
            _make_handler(hass, func, returns),
            schema=vol.Schema({**QUETY, **fields}),
            supports_response=SupportsResponse.OPTIONAL if returns else SupportsResponse.NONE,
        )
    return True


def _make_handler(hass: HomeAssistant, func: Call, returns: bool):
    async def handle(call: ServiceCall) -> ServiceResponse:
        client = _get_client(hass, call.data.get("quety"))
        result = await func(client, call.data)
        return {"response": result} if returns else None

    return handle


def _get_client(hass: HomeAssistant, quety: str | None) -> CueyClient:
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    if quety:
        entries = [entry for entry in entries if entry.title.lower() == quety.lower()]
    if not entries:
        raise HomeAssistantError("Geen geladen Quety gevonden die bij deze actie past")
    if len(entries) > 1:
        raise HomeAssistantError("Meerdere Quety's gevonden: geef de naam mee met 'quety'")
    return entries[0].runtime_data


async def async_setup_entry(hass: HomeAssistant, entry: CueyConfigEntry) -> bool:
    client = CueyClient(
        hass,
        entry.data[CONF_HOST],
        entry.data[CONF_PORT],
        demo=entry.data.get(CONF_DEMO, False),
    )
    try:
        await client.hello()
    except CueyError as err:
        raise ConfigEntryNotReady(str(err)) from err

    entry.runtime_data = client
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_options_updated(hass: HomeAssistant, entry: CueyConfigEntry) -> None:
    """Playbacks aangepast: herlaad zodat de entiteiten kloppen."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: CueyConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)