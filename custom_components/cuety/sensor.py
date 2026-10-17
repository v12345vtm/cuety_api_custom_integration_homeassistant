# Cuety-integratie, versie 5.0.0
"""Tekstentiteit httpresponse: het antwoord van de Quety op het laatste commando."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CueyConfigEntry
from .api import CueyClient
from .const import antwoord_signal
from .entity import CueyEntity

MAX_STATE_LENGTH = 255  # de maximale lengte van een entiteitsstatus in Home Assistant


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CueyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([CueyHttpResponseSensor(entry, entry.runtime_data)])


class CueyHttpResponseSensor(CueyEntity, SensorEntity):
    _attr_name = "httpresponse"
    _attr_icon = "mdi:web"

    def __init__(self, entry: CueyConfigEntry, client: CueyClient) -> None:
        super().__init__(entry, client)
        self._attr_unique_id = f"{entry.entry_id}_httpresponse"
        self._attr_native_value = None
        self._commando: str | None = None
        self._volledig: str | None = None
        self._signal = antwoord_signal(entry.entry_id)

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(async_dispatcher_connect(self.hass, self._signal, self._ontvang))

    @callback
    def _ontvang(self, commando: str, antwoord: str) -> None:
        self._commando = commando
        self._volledig = antwoord
        self._attr_native_value = antwoord.replace("\n", " ").strip()[:MAX_STATE_LENGTH]
        self.async_write_ha_state()

    @property
    def extra_state_attributes(self) -> dict[str, str | None]:
        return {"commando": self._commando, "volledig_antwoord": self._volledig}
