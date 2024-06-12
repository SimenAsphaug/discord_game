import logging
from typing import Optional, Dict, Any
import homeassistant.helpers.config_validation as cv
import nextcord
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.helpers import selector
from nextcord import LoginFailure
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

AUTH_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ACCESS_TOKEN): cv.string
    }
)

class DiscordGameConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        errors: Dict[str, str] = {}
        if user_input is not None:
            try:
                await self.validate_auth(user_input[CONF_ACCESS_TOKEN])
            except ValueError:
                errors["base"] = "auth"
            if not errors:
                return self.async_create_entry(title="Discord Game", data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=AUTH_SCHEMA, errors=errors
        )

    async def validate_auth(self, token: str) -> None:
        client = nextcord.Client(intents=nextcord.Intents.all())
        try:
            await client.login(token)
            await client.close()
        except LoginFailure:
            raise ValueError
