# Cuety-integratie, versie 4.0.0
"""Schakelaars: blackout en per playback (aan = Go+, uit = release)."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import STATE_ON
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
    entities: list[SwitchEntity] = [CueyBlackoutSwitch(entry, client)]
    entities += [
        CueyPlaybackSwitch(entry, client, playback)
        for playback in entry.options.get(CONF_PLAYBACKS, [])
    ]
    async_add_entities(entities)


class _CueySwitchBase(CueyEntity, SwitchEntity, RestoreEntity):
    """Onthoudt de laatste stand na een herstart, net als een input_boolean."""

    _attr_is_on = False

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if (last := await self.async_get_last_state()) is not None:
            self._attr_is_on = last.state == STATE_ON


class CueyBlackoutSwitch(_CueySwitchBase):
    _attr_name = "Blackout"

    def __init__(self, entry: CueyConfigEntry, client: CueyClient) -> None:
        super().__init__(entry, client)
        self._attr_unique_id = f"{entry.entry_id}_blackout"

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._client.blackout(True)
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._client.blackout(False)
        self._attr_is_on = False
        self.async_write_ha_state()


class CueyPlaybackSwitch(_CueySwitchBase):
    def __init__(self, entry: CueyConfigEntry, client: CueyClient, playback: int) -> None:
        super().__init__(entry, client)
        self._playback = playback
        self._attr_name = f"Playback {playback}"
        self._attr_unique_id = f"{entry.entry_id}_playback_{playback}"

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._client.go(self._playback)
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._client.release(self._playback)
        self._attr_is_on = False
        self.async_write_ha_state()