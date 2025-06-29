# =============================================================================
# number.py - Number Entities
# =============================================================================

"""Support for Jablotron Futura number entities."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, HOLDING_REGISTERS
from .coordinator import JablotronFuturaCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Jablotron Futura number entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Time-based function controls
    time_registers = [
        "boost_time",
        "circulation_time", 
        "overpressure_time",
        "night_time",
        "party_time",
    ]

    entities = []
    for register_key in time_registers:
        entities.append(JablotronFuturaTimeNumber(coordinator, register_key))

    # Add zone button timer numbers if VarioBreeze is supported
    variobreeze_supported = coordinator.data.get("config_variobreeze_supported", False)
    if variobreeze_supported:
        for zone in range(1, 9):
            zone_button_present = coordinator.data.get(f"zone_{zone}_button_present", False)
            if zone_button_present:
                entities.append(JablotronFuturaZoneButtonTimerNumber(coordinator, zone))

    async_add_entities(entities)


class JablotronFuturaBaseNumber(CoordinatorEntity, NumberEntity):
    """Base class for Jablotron Futura number entities."""

    def __init__(
        self,
        coordinator: JablotronFuturaCoordinator,
        register_key: str,
    ) -> None:
        """Initialize the number."""
        super().__init__(coordinator)
        self._register_key = register_key
        self._config = HOLDING_REGISTERS.get(register_key, {})
        
        self._attr_unique_id = f"{coordinator.host}_{register_key}"
        self._attr_name = self._config.get("name", register_key)
        self._attr_mode = NumberMode.BOX

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        # This will be implemented by subclasses
        raise NotImplementedError


class JablotronFuturaTimeNumber(JablotronFuturaBaseNumber):
    """Time-based number entity for Jablotron Futura."""

    def __init__(
        self, 
        coordinator: JablotronFuturaCoordinator,
        register_key: str
    ) -> None:
        """Initialize the time number."""
        super().__init__(coordinator, register_key)
        
        self._attr_native_min_value = self._config.get("min", 0)
        self._attr_native_max_value = self._config.get("max", 7200)
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = UnitOfTime.SECONDS
        
        # Set appropriate icons
        icon_map = {
            "boost_time": "mdi:timer",
            "circulation_time": "mdi:timer", 
            "overpressure_time": "mdi:timer",
            "night_time": "mdi:weather-night",
            "party_time": "mdi:party-popper",
        }
        self._attr_icon = icon_map.get(register_key, "mdi:timer")

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        value = self.coordinator.data.get(self._register_key)
        return float(value) if value is not None else None

    async def async_set_native_value(self, value: float) -> None:
        """Set the time value."""
        int_value = int(value)
        address = self._config["address"]
        success = await self.coordinator.async_write_register(address, int_value)
        if not success:
            _LOGGER.error("Failed to set %s to %d", self._attr_name, int_value)


class JablotronFuturaZoneButtonTimerNumber(JablotronFuturaBaseNumber):
    """Zone button timer number for Jablotron Futura."""

    def __init__(
        self, 
        coordinator: JablotronFuturaCoordinator,
        zone: int
    ) -> None:
        """Initialize the zone button timer number."""
        super().__init__(coordinator, f"zone_{zone}_button_timer")
        self._zone = zone
        self._attr_name = f"Zone {zone} Button Timer"
        
        self._attr_native_min_value = 0
        self._attr_native_max_value = 10800  # 3 hours
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = UnitOfTime.SECONDS
        self._attr_icon = "mdi:timer"

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        value = self.coordinator.data.get(f"zone_{self._zone}_button_timer")
        return float(value) if value is not None else None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data.get(f"zone_{self._zone}_button_present", False)
        )

    async def async_set_native_value(self, value: float) -> None:
        """Set the timer value."""
        int_value = int(value)
        address = 402 + (self._zone - 1) * 10  # Button timer register address
        success = await self.coordinator.async_write_register(address, int_value)
        if not success:
            _LOGGER.error("Failed to set zone %d button timer to %d", self._zone, int_value)
