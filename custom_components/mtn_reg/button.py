import aiohttp
from homeassistant.components.button import ButtonEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Henter listen over enheter (dører) senteret faktisk har, og lager
    # én knapp PER enhet - i stedet for én knapp som prøvde å åpne alt
    # samtidig. Kjøres kun én gang ved oppstart (enhetslisten endrer seg
    # sjelden); nye enheter krever en reload av integrasjonen i HA.
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{coordinator.api_url}/ha/enheter",
            headers={"x-ha-api-key": coordinator.api_key},
            timeout=aiohttp.ClientTimeout(total=10),
        ) as resp:
            resp.raise_for_status()
            enheter = await resp.json()

    async_add_entities([ApneDorKnapp(coordinator, entry, e["id"], e["navn"]) for e in enheter])


class ApneDorKnapp(ButtonEntity):
    def __init__(self, coordinator, entry, enhet_id, enhet_navn):
        self._coordinator = coordinator
        self._enhet_id = enhet_id
        self._attr_name = f"MTN-reg Åpne dør - {enhet_navn}"
        self._attr_unique_id = f"{entry.entry_id}_apne_dor_{enhet_id}"
        self._attr_icon = "mdi:door-open"

    async def async_press(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self._coordinator.api_url}/ha/apne-dor/{self._enhet_id}",
                headers={"x-ha-api-key": self._coordinator.api_key},
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                resp.raise_for_status()
