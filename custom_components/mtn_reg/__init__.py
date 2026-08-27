import logging
from datetime import timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_API_URL, CONF_API_KEY

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor", "button"]


class MtnRegCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, api_url: str, api_key: str):
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(minutes=2))
        self.api_url = api_url
        self.api_key = api_key

    async def _async_update_data(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/ha/statistikk",
                    headers={"x-ha-api-key": self.api_key},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status != 200:
                        raise UpdateFailed(f"Uventet statuskode: {resp.status}")
                    return await resp.json()
        except aiohttp.ClientError as feil:
            raise UpdateFailed(f"Kunne ikke nå MTN-registrering: {feil}") from feil


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = MtnRegCoordinator(hass, entry.data[CONF_API_URL], entry.data[CONF_API_KEY])
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded
