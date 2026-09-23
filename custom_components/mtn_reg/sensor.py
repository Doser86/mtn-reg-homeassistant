from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

SENSOR_TYPER = {
    "totaltAntallMedlemmer": "Totalt antall medlemmer",
    "innsjekketIDag": "Innsjekket i dag",
    "innsjekket48t": "Innsjekket siste 48 timer",
    "innsjekketUke": "Innsjekket siste uke",
    "kapasitet": "Kapasitet (maks)",
    "inneNaa": "Personer inne nå",
    "kapasitetProsent": "Kapasitet fylt",
}

# Egne ikoner/enheter for kapasitet-sensorene - resten bruker standard
# account-group-ikon uten enhet.
SENSOR_IKON_OVERSTYRING = {
    "kapasitet": "mdi:account-multiple",
    "inneNaa": "mdi:account-check",
    "kapasitetProsent": "mdi:gauge",
}
SENSOR_ENHET_OVERSTYRING = {
    "kapasitetProsent": "%",
}


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entiteter = [MtnRegSensor(coordinator, entry, nokkel, navn) for nokkel, navn in SENSOR_TYPER.items()]
    async_add_entities(entiteter)


class MtnRegSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry, nokkel, navn):
        super().__init__(coordinator)
        self._nokkel = nokkel
        self._attr_name = f"MTN-reg {navn}"
        self._attr_unique_id = f"{entry.entry_id}_{nokkel}"
        self._attr_icon = SENSOR_IKON_OVERSTYRING.get(nokkel, "mdi:account-group")
        if nokkel in SENSOR_ENHET_OVERSTYRING:
            self._attr_native_unit_of_measurement = SENSOR_ENHET_OVERSTYRING[nokkel]

    @property
    def native_value(self):
        return self.coordinator.data.get(self._nokkel)
