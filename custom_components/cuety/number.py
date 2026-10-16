"""Intensiteit per playback, 0 tot 100 %."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from . import CueyConfigEntry
from .api import CueyClient
from .const import CONF_PLAYBACKS
from .entity import CueyEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CueyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    client = entry.runtime_data
    async_add_entities(
        [
            CueyIntensityNumber(entry, client, playback)
            for playback in entry.options.get(CONF_PLAYBACKS, [])
        ]
    )


class CueyIntensityNumber(CueyEntity, NumberEntity, RestoreEntity):
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_mode = NumberMode.SLIDER

    def __init__(self, entry: CueyConfigEntry, client: CueyClient, playback: int) -> None:
        super().__init__(entry, client)
        self._playback = playback
        self._attr_name = f"Playback {playback} intensiteit"
        self._attr_unique_id = f"{entry.entry_id}_playback_{playback}_intensity"

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if (last := await self.async_get_last_state()) is not None:
            try:
                self._attr_native_value = float(last.state)
            except ValueError:
                pass

    async def async_set_native_value(self, value: float) -> None:
        await self._client.set_intensity(self._playback, value / 100)
        self._attr_native_value = value
        self.async_write_ha_state()
