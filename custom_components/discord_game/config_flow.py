import logging
from typing import Optional, Dict, Any

import homeassistant.helpers.config_validation as cv
import nextcord
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.helpers import selector
from nextcord import LoginFailure

from .const import DOMAIN, CONF_MEMBERS, CONF_CHANNELS, CONF_IMAGE_FORMAT

_LOGGER = logging.getLogger(__name__)

AUTH_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ACCESS_TOKEN): cv.string,
        vol.Required(CONF_IMAGE_FORMAT, default='webp'): selector.SelectSelector(
            selector.SelectSelectorConfig(options=['png', 'webp', 'jpeg', 'jpg'],
                                          multiple=False,
                                          mode=selector.SelectSelectorMode.DROPDOWN),
        ),
    }
)

class DiscordGameConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        errors: Dict[str, str] = {}
        if user_input is not None:
            try:
                await self.validate_auth_and_fetch_data(user_input[CONF_ACCESS_TOKEN])
            except ValueError:
                errors["base"] = "auth"
            if not errors:
                self.data = user_input
                self.data[CONF_MEMBERS] = []
                self.data[CONF_CHANNELS] = []

                return await self.async_step_members()

        return self.async_show_form(
            step_id="user", data_schema=AUTH_SCHEMA, errors=errors
        )

    async def async_step_members(self, user_input: Optional[Dict[str, Any]] = None):
        _MEMBERS_SCHEMA = vol.Schema(
            {
                vol.Optional(CONF_MEMBERS): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=userNames,
                                                  multiple=True,
                                                  mode=selector.SelectSelectorMode.DROPDOWN),
                ),
                vol.Optional(CONF_CHANNELS): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=channelNames,
                                                  multiple=True,
                                                  mode=selector.SelectSelectorMode.DROPDOWN),
                ),
            }
        )

        errors: Dict[str, str] = {}
        if user_input is not None:
            for user in user_input.get(CONF_MEMBERS, []):
                self.data[CONF_MEMBERS].append(members.get(user).id)
            if user_input.get(CONF_CHANNELS):
                for channel in user_input.get(CONF_CHANNELS, []):
                    self.data[CONF_CHANNELS].append(channels.get(channel).id)

            return self.async_create_entry(title="Discord Game", data=self.data)

        return self.async_show_form(
            step_id="members", data_schema=_MEMBERS_SCHEMA, errors=errors
        )

    async def validate_auth_and_fetch_data(self, token: str) -> None:
        global client, members, userNames, channels, channelNames
        client = nextcord.Client(intents=nextcord.Intents.all())
        members = {}
        userNames = []
        channels = {}
        channelNames = []

        try:
            await client.login(token)
            guilds = await client.fetch_guilds().flatten()
            _LOGGER.debug("guilds: %s", guilds)

            for guild in guilds:
                _members = await guild.fetch_members().flatten()
                for member in _members:
                    members[member.name] = member

            for guild in guilds:
                _channels = await guild.fetch_channels()
                for channel in _channels:
                    channels[channel.name] = channel

            userNames = list(dict.fromkeys([member.name for member in members.values()]))
            channelNames = list(dict.fromkeys([channel.name for channel in channels.values()]))
            _LOGGER.debug("userNames: %s", userNames)
            _LOGGER.debug("channelNames: %s", channelNames)

            await client.close()
        except LoginFailure:
            raise ValueError
        except Exception as e:
            _LOGGER.error("Unexpected error: %s", e)
            raise ValueError
