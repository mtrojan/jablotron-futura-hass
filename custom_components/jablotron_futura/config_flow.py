"""Config flow for Jablotron Futura integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import CONF_SLAVE_ID, DEFAULT_NAME, DEFAULT_PORT, DEFAULT_SLAVE_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): int,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    host = data[CONF_HOST]
    port = data[CONF_PORT]
    slave_id = data[CONF_SLAVE_ID]

    # Test the connection
    client = ModbusTcpClient(host=host, port=port, timeout=10)
    
    try:
        connection = await hass.async_add_executor_job(client.connect)
        if not connection:
            raise CannotConnect("Unable to connect to Modbus TCP")
        
        # Try to read device ID to verify it's a Jablotron Futura
        result = await hass.async_add_executor_job(
            client.read_input_registers, 0, 1, slave_id
        )
        
        if result.isError():
            raise CannotConnect("Unable to read from device")
            
        device_id = result.registers[0]
        if device_id != 39:  # Jablotron Futura device ID
            _LOGGER.warning("Device ID %d doesn't match Jablotron Futura (39)", device_id)
        
        # Read serial number for unique ID
        result = await hass.async_add_executor_job(
            client.read_input_registers, 1, 2, slave_id
        )
        
        if result.isError():
            raise CannotConnect("Unable to read serial number")
            
        serial_number = (result.registers[0] << 16) | result.registers[1]
        
    except ModbusException as ex:
        _LOGGER.error("Error connecting to Jablotron Futura: %s", ex)
        raise CannotConnect("Connection error") from ex
    finally:
        client.close()

    # Return info that you want to store in the config entry.
    return {
        "title": data[CONF_NAME],
        "serial_number": serial_number,
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Jablotron Futura."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Create unique ID from host and serial number
                unique_id = f"{user_input[CONF_HOST]}_{info['serial_number']}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
