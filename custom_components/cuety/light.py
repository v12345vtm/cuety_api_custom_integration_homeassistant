# Cuety-integratie, versie 5.0.0
"""Light per playback: aan is Go+, uit is release, de helderheid is de intensiteit."""
from __future__ import annotations

from typing import Any

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CueyConfigEntry
from .api import CueyClient, CueyError
from .const import CONF_PLAYBACKS, refresh_signal
from .entity import CueyEntity


def _naar_intensiteit(brightness: int) -> float:
    """Helderheid van Home Assistant (0 t/m 255) wordt intensiteit van de Quety (0 t/m 1)."""
    return round(brightness / 255, 2)


def _naar_brightness(intensiteit: float) -> int:
    """Intensiteit van de Quety (0 t/m 1) wordt helderheid van Home Assistant (0 t/m 255)."""
    return max(0, min(255, round(intensiteit * 255)))


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CueyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    client = entry.runtime_data
    async_add_entities(
        [
            CueyPlaybackLight(entry, client, playback)
            for playback in entry.options.get(CONF_PLAYBACKS, [])
        ]
    )


class CueyPlaybackLight(CueyEntity, LightEntity):
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_color_mode = ColorMode.BRIGHTNESS

    def __init__(self, entry: CueyConfigEntry, client: CueyClient, playback: int) -> None:
        super().__init__(entry, client)
        self._playback = playback
        self._attr_name = f"Playback {playback}"
        self._attr_unique_id = f"{entry.entry_id}_playback_{playback}_light"
        self._attr_is_on = None
        self._attr_brightness = None
        self._signal = refresh_signal(entry.entry_id)

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(async_dispatcher_connect(self.hass, self._signal, self._verversen))
        self.async_schedule_update_ha_state(True)

    @callback
    def _verversen(self, payload: Any) -> None:
        """Na een service of knop: alleen deze playback (een nummer) of alle playbacks (None)."""
        if payload is None or payload == self._playback:
            self.async_schedule_update_ha_state(True)

    async def async_update(self) -> None:
        """Haalt de stand op bij de Quety. Geeft het geen waarde, dan blijft de bestaande stand."""
        try:
            actief = await self._client.get_playback_active(self._playback)
            intensiteit = await self._client.get_playback_intensity(self._playback)
        except (CueyError, TypeError, ValueError):
            self._attr_available = False
            return
        self._attr_available = True
        if actief is not None:
            self._attr_is_on = actief
        if intensiteit is not None:
            self._attr_brightness = _naar_brightness(intensiteit)

    async def async_turn_on(self, **kwargs: Any) -> None:
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        if brightness is not None:
            await self._client.set_intensity(self._playback, _naar_intensiteit(brightness))
            self._attr_brightness = brightness
        if not self._attr_is_on:
            # Go+ zet de cue door. Daarom alleen als de playback nog uit staat.
            await self._client.go(self._playback)
            self._attr_is_on = True
        await self.async_update_ha_state(force_refresh=True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._client.release(self._playback)
        self._attr_is_on = False
        await self.async_update_ha_state(force_refresh=True)
