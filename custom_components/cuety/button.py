"""Knoppen."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CueyConfigEntry
from .api import CueyClient
from .entity import CueyEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CueyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([CueyReleaseAllButton(entry, entry.runtime_data)])


class CueyReleaseAllButton(CueyEntity, ButtonEntity):
    _attr_name = "Release alle playbacks"

    def __init__(self, entry: CueyConfigEntry, client: CueyClient) -> None:
        super().__init__(entry, client)
        self._attr_unique_id = f"{entry.entry_id}_release_all"

    async def async_press(self) -> None:
        await self._client.release_all()