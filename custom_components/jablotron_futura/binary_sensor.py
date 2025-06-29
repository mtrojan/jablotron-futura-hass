"""Support for Jablotron Futura binary sensors."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import JablotronFuturaCoordinator
from .zones import (
    JablotronFuturaModeBinarySensor,
    JablotronFuturaErrorBinarySensor,
    JablotronFuturaWarningBinarySensor,
    JablotronFuturaConfigBinarySensor,
    JablotronFuturaZoneBinarySensor,
    JablotronFuturaZoneButtonPresenceSensor,
    JablotronFuturaZoneButtonActiveSensor,
    JablotronFuturaSensorPresenceSensor,
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Jablotron Futura binary sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Import all binary sensor classes from zones.py and create entities
    # This setup is handled in the zones.py file
    
    from .zones import async_setup_binary_sensors
    await async_setup_binary_sensors(hass, config_entry, async_add_entities)
