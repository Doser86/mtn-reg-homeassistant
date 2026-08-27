import aiohttp
from homeassistant.components.button import ButtonEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ApneDorKnapp(coordinator, entry)])


class ApneDorKnapp(ButtonEntity):
    def __init__(self, coordinator, entry):
        self._coordinator = coordinator
        self._attr_name = "MTN-reg Åpne dør (prøvetime/besøk)"
        self._attr_unique_id = f"{entry.entry_id}_apne_dor"
        self._attr_icon = "mdi:door-open"

    async def async_press(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self._coordinator.api_url}/ha/apne-dor",
                headers={"x-ha-api-key": self._coordinator.api_key},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                resp.raise_for_status()
