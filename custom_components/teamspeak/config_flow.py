"""Config flow for the Teamspeak 3 Server integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import (
    TeamspeakApiClient,
    TeamspeakApiClientAuthenticationError,
    TeamspeakApiClientCommunicationError,
    TeamspeakData,
)
from .const import DOMAIN

DEFAULT_USERNAME = "serveradmin"
DESCRIPTION_URL = "https://gitlab.p4nto.de/p4nto/homeassistant-teamspeak"


class TeamspeakFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for a TeamSpeak 3 Server."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                data = await self._async_validate_input(
                    user_input[CONF_HOST],
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                )
            except TeamspeakApiClientAuthenticationError:
                errors["base"] = "invalid_auth"
            except TeamspeakApiClientCommunicationError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(data["serverinfo"]["unique_identifier"])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=data["serverinfo"]["name"] or user_input[CONF_HOST],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=self._async_get_schema(user_input),
            description_placeholders={"documentation_url": DESCRIPTION_URL},
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Handle re-authentication with the TeamSpeak server."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle re-authentication input."""
        errors: dict[str, str] = {}
        reauth_entry = self._get_reauth_entry()

        if user_input is not None:
            try:
                data = await self._async_validate_input(
                    reauth_entry.data[CONF_HOST],
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                )
            except TeamspeakApiClientAuthenticationError:
                errors["base"] = "invalid_auth"
            except TeamspeakApiClientCommunicationError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_update_reload_and_abort(
                    reauth_entry,
                    unique_id=data["serverinfo"]["unique_identifier"],
                    data_updates={
                        CONF_USERNAME: user_input[CONF_USERNAME],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                    },
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_USERNAME,
                        default=reauth_entry.data[CONF_USERNAME],
                    ): TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT)),
                    vol.Required(CONF_PASSWORD): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.PASSWORD)
                    ),
                }
            ),
            description_placeholders={
                CONF_HOST: reauth_entry.data[CONF_HOST],
            },
            errors=errors,
        )

    def _async_get_schema(self, user_input: dict[str, Any] | None) -> vol.Schema:
        """Return the user schema."""
        defaults = user_input or {}
        return vol.Schema(
            {
                vol.Required(
                    CONF_HOST,
                    default=defaults.get(CONF_HOST, ""),
                ): TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT)),
                vol.Required(
                    CONF_USERNAME,
                    default=defaults.get(CONF_USERNAME, DEFAULT_USERNAME),
                ): TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT)),
                vol.Required(CONF_PASSWORD): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.PASSWORD)
                ),
            }
        )

    async def _async_validate_input(
        self, host: str, username: str, password: str
    ) -> TeamspeakData:
        """Validate the credentials and return the server data."""
        client = TeamspeakApiClient(host, username, password)
        try:
            data = await self.hass.async_add_executor_job(client.get_data)
        finally:
            await self.hass.async_add_executor_job(client.close)

        if not data["serverinfo"]["unique_identifier"]:
            raise TeamspeakApiClientCommunicationError(
                "The TeamSpeak server did not return a unique identifier"
            )
        return data
