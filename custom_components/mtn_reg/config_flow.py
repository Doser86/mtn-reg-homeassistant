import voluptuous as vol
import aiohttp
from homeassistant import config_entries
from .const import DOMAIN, CONF_API_URL, CONF_API_KEY, DEFAULT_API_URL


class MtnRegConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            gyldig = await self._test_nokkel(user_input[CONF_API_URL], user_input[CONF_API_KEY])
            if gyldig:
                return self.async_create_entry(title="MTN-registrering", data=user_input)
            errors["base"] = "invalid_auth"

        skjema = vol.Schema({
            vol.Required(CONF_API_URL, default=DEFAULT_API_URL): str,
            vol.Required(CONF_API_KEY): str,
        })
        return self.async_show_form(step_id="user", data_schema=skjema, errors=errors)

    async def _test_nokkel(self, api_url: str, api_key: str) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{api_url}/ha/statistikk",
                    headers={"x-ha-api-key": api_key},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    return resp.status == 200
        except Exception:
            return False
