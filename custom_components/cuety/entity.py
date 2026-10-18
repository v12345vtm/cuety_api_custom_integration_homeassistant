# Cuety-integratie, versie 5.2.0
"""Basis voor alle Cuety-entiteiten."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .api import CueyClient
from .const import DOMAIN


class CueyEntity(Entity):
    """Gedeelde eigenschappen. De stand wordt per entiteit opgehaald, niet vanzelf (geen polling)."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_assumed_state = False

    def __init__(self, entry: ConfigEntry, client: CueyClient) -> None:
        self._client = client
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Visual Productions",
            model="Cuety (LPU-2)",
            configuration_url=f"http://{client.host}:{client.port}",
        )
