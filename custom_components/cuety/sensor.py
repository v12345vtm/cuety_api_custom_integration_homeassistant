# Cuety-integratie, versie 4.0.0
"""Tekstentiteit met het laatste antwoord van de Quety."""
from __future__ import annotations

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
    async_add_entities([CueyLaatsteAntwoordSensor(entry, entry.runtime_data)])


class CueyLaatsteAntwoordSensor(CueyEntity, SensorEntity):
    _attr_name = "Laatste antwoord"
    _attr_icon = "mdi:message-text-outline"

    def __init__(self, entry: CueyConfigEntry, client: CueyClient) -> None:
        super().__init__(entry, client)
        self._attr_unique_id = f"{entry.entry_id}_laatste_antwoord"
        self._signal = antwoord_signal(entry.entry_id)
        self._commando: str | None = None
        self._volledig: str | None = None

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(self.hass, self._signal, self._ontvang)
        )

    @callback
    def _ontvang(self, commando: str, antwoord: str) -> None:
        self._commando = commando
        self._volledig = antwoord
        self._attr_native_value = antwoord.replace("\n", " ").strip()[:MAX_STATE_LENGTH]
        self.async_write_ha_state()

    @property
    def extra_state_attributes(self) -> dict[str, str | None]:
        return {"commando": self._commando, "volledig_antwoord": self._volledig}
