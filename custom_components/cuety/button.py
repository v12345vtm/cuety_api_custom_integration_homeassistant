# Cuety-integratie, versie 5.0.0
"""Knoppen: release alle playbacks, hello en status opvragen."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CueyConfigEntry
from .api import CueyClient
from .const import refresh_signal
from .entity import CueyEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CueyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    client = entry.runtime_data
    async_add_entities(
        [
            CueyReleaseAllButton(entry, client),
            CueyHelloButton(entry, client),
            CueyStatusButton(entry, client),
        ]
    )


class CueyReleaseAllButton(CueyEntity, ButtonEntity):
    _attr_name = "Release alle playbacks"

    def __init__(self, entry: CueyConfigEntry, client: CueyClient) -> None:
        super().__init__(entry, client)
        self._attr_unique_id = f"{entry.entry_id}_release_all"
        self._signal = refresh_signal(entry.entry_id)

    async def async_press(self) -> None:
        await self._client.release_all()
        async_dispatcher_send(self.hass, self._signal, None)


class CueyHelloButton(CueyEntity, ButtonEntity):
    """Stuurt /ajax/hello. Het antwoord komt in httpresponse."""

    _attr_name = "Hello"

    def __init__(self, entry: CueyConfigEntry, client: CueyClient) -> None:
        super().__init__(entry, client)
        self._attr_unique_id = f"{entry.entry_id}_hello"

    async def async_press(self) -> None:
        await self._client.hello()


class CueyStatusButton(CueyEntity, ButtonEntity):
    """Stuurt /ajax/pbxx/ac en ververst daarna de stand van alle lights."""

    _attr_name = "Status opvragen"

    def __init__(self, entry: CueyConfigEntry, client: CueyClient) -> None:
        super().__init__(entry, client)
        self._attr_unique_id = f"{entry.entry_id}_status"
        self._signal = refresh_signal(entry.entry_id)

    async def async_press(self) -> None:
        await self._client.get_active_status()
        async_dispatcher_send(self.hass, self._signal, None)
