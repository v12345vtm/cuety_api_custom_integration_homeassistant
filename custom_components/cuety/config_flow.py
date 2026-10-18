# Cuety-integratie, versie 5.1.0
"""Installatie en opties van de Cuety-integratie."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .api import CueyClient, CueyError
from .const import (
    CONF_DEMO,
    CONF_HOST,
    CONF_NAME,
    CONF_PLAYBACKS,
    CONF_PORT,
    DEFAULT_PORT,
    DOMAIN,
    MAX_PLAYBACK,
)


def parse_playbacks(text: str) -> list[int]:
    """'11' is playbacks 1 t/m 11, '5-11' is playbacks 5 t/m 11. Geeft ValueError bij ongeldige invoer."""
    cleaned = text.strip().lower().replace("t/m", "-").replace(" ", "")
    if "-" in cleaned:
        first, last = cleaned.split("-", 1)
        start, end = int(first), int(last)
    else:
        start, end = 1, int(cleaned)
    if not 1 <= start <= end <= MAX_PLAYBACK:
        raise ValueError("bereik buiten 1 t/m 99 of omgekeerd")
    return list(range(start, end + 1))


def format_playbacks(numbers: list[int]) -> str:
    """Zet de opgeslagen lijst terug in de invoer: 1 t/m 11 wordt '11', 5 t/m 11 wordt '5-11'."""
    if not numbers:
        return ""
    ordered = sorted(numbers)
    start, end = ordered[0], ordered[-1]
    if ordered != list(range(start, end + 1)):
        return ""
    return str(end) if start == 1 else f"{start}-{end}"


class CueyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = user_input[CONF_PORT]
            demo = user_input.get(CONF_DEMO, False)
            await self.async_set_unique_id(f"{host}:{port}")
            self._abort_if_unique_id_configured()

            try:
                await CueyClient(self.hass, host, port, demo=demo).hello()
            except CueyError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_NAME].strip(),
                    data={CONF_HOST: host, CONF_PORT: port, CONF_DEMO: demo},
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default="Cuety"): str,
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Optional(CONF_DEMO, default=False): bool,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> CueyOptionsFlow:
        return CueyOptionsFlow()


class CueyOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                playbacks = parse_playbacks(user_input[CONF_PLAYBACKS])
            except ValueError:
                errors["base"] = "invalid_playbacks"
            else:
                return self.async_create_entry(data={CONF_PLAYBACKS: playbacks})

        current = format_playbacks(self.config_entry.options.get(CONF_PLAYBACKS, []))
        schema = vol.Schema({vol.Optional(CONF_PLAYBACKS, default=current): str})
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
