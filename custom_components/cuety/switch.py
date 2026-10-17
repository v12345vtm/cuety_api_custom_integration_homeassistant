# Cuety-integratie, versie 5.0.0
"""Schakelaar voor de blackout van de Quety."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CueyConfigEntry
from .api import CueyClient, CueyError
from .const import refresh_signal
from .entity import CueyEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CueyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([CueyBlackoutSwitch(entry, entry.runtime_data)])


class CueyBlackoutSwitch(CueyEntity, SwitchEntity):
    _attr_name = "Blackout"

    def __init__(self, entry: CueyConfigEntry, client: CueyClient) -> None:
        super().__init__(entry, client)
        self._attr_unique_id = f"{entry.entry_id}_blackout"
        self._attr_is_on = None
        self._signal = refresh_signal(entry.entry_id)

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(async_dispatcher_connect(self.hass, self._signal, self._verversen))
        self.async_schedule_update_ha_state(True)

    @callback
    def _verversen(self, payload: Any) -> None:
        if payload == "blackout":
            self.async_schedule_update_ha_state(True)

    async def async_update(self) -> None:
        try:
            stand = await self._client.get_blackout()
        except CueyError:
            self._attr_available = False
            return
        self._attr_available = True
        if stand is not None:
            self._attr_is_on = stand

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._client.blackout(True)
        self._attr_is_on = True
        await self.async_update_ha_state(force_refresh=True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._client.blackout(False)
        self._attr_is_on = False
        await self.async_update_ha_state(force_refresh=True)
