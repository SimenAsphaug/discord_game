import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.helpers import selector
from .const import DOMAIN

class DiscordGameConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Discord Game", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_ACCESS_TOKEN): str
            }
        )
        return self.async_show_form(step_id="user", data_schema=data_schema)
