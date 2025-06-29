# =============================================================================
# zone.py - Zone Control Entities  
# =============================================================================

"""Support for Jablotron Futura VarioBreeze zone control."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ZONE_BUTTON_MODES
from .coordinator import JablotronFuturaCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Jablotron Futura zone entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []

    # Create zone entities for each zone (1-8)
    for zone in range(1, 9):
        # Zone sensor entities
        entities.extend([
            JablotronFuturaZoneTemperatureSensor(coordinator, zone),
            JablotronFuturaZoneHumiditySensor(coordinator, zone),
            JablotronFuturaZoneCO2Sensor(coordinator, zone),
            JablotronFuturaZoneFloorTemperatureSensor(coordinator, zone),
        ])
        
        # Zone control entities
        entities.extend([
            JablotronFuturaZoneButtonModeSelect(coordinator, zone),
            JablotronFuturaZoneButtonTimerNumber(coordinator, zone),
            JablotronFuturaZoneButtonActiveSwitch(coordinator, zone),
        ])

    async_add_entities(entities)


class JablotronFuturaZoneBaseEntity(CoordinatorEntity):
    """Base class for Jablotron Futura zone entities."""

    def __init__(
        self,
        coordinator: JablotronFuturaCoordinator,
        zone: int,
        entity_type: str,
    ) -> None:
        """Initialize the zone entity."""
        super().__init__(coordinator)
        self._zone = zone
        self._entity_type = entity_type
        
        self._attr_unique_id = f"{coordinator.host}_zone_{zone}_{entity_type}"
        self._attr_name = f"Zone {zone} {entity_type.replace('_', ' ').title()}"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Zone entities are only available if zone sensors/buttons are present
        if "button" in self._entity_type:
            return (
                self.coordinator.last_update_success
                and self.coordinator.data.get(f"zone_{self._zone}_button_present", False)
            )
        else:
            return (
                self.coordinator.last_update_success
                and self.coordinator.data.get(f"zone_{self._zone}_sensors_present", False)
            )


class JablotronFuturaZoneTemperatureSensor(JablotronFuturaZoneBaseEntity, SensorEntity):
    """Zone temperature sensor for Jablotron Futura."""

    def __init__(self, coordinator: JablotronFuturaCoordinator, zone: int) -> None:
        """Initialize the zone temperature sensor."""
        super().__init__(coordinator, zone, "temperature")
        self._attr_device_class = "temperature"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_icon = "mdi:thermometer"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get(f"zone_{self._zone}_temperature")


class JablotronFuturaZoneHumiditySensor(JablotronFuturaZoneBaseEntity, SensorEntity):
    """Zone humidity sensor for Jablotron Futura."""

    def __init__(self, coordinator: JablotronFuturaCoordinator, zone: int) -> None:
        """Initialize the zone humidity sensor."""
        super().__init__(coordinator, zone, "humidity")
        self._attr_device_class = "humidity"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_icon = "mdi:water-percent"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get(f"zone_{self._zone}_humidity")


class JablotronFuturaZoneCO2Sensor(JablotronFuturaZoneBaseEntity, SensorEntity):
    """Zone CO2 sensor for Jablotron Futura."""

    def __init__(self, coordinator: JablotronFuturaCoordinator, zone: int) -> None:
        """Initialize the zone CO2 sensor."""
        super().__init__(coordinator, zone, "co2")
        self._attr_device_class = "carbon_dioxide"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = CONCENTRATION_PARTS_PER_MILLION
        self._attr_icon = "mdi:molecule-co2"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get(f"zone_{self._zone}_co2")


class JablotronFuturaZoneFloorTemperatureSensor(JablotronFuturaZoneBaseEntity, SensorEntity):
    """Zone floor temperature sensor for Jablotron Futura."""

    def __init__(self, coordinator: JablotronFuturaCoordinator, zone: int) -> None:
        """Initialize the zone floor temperature sensor."""
        super().__init__(coordinator, zone, "floor_temperature")
        self._attr_device_class = "temperature"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_icon = "mdi:thermometer-lines"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get(f"zone_{self._zone}_floor_temperature")


class JablotronFuturaZoneButtonModeSelect(JablotronFuturaZoneBaseEntity, SelectEntity):
    """Zone button mode select for Jablotron Futura."""

    def __init__(self, coordinator: JablotronFuturaCoordinator, zone: int) -> None:
        """Initialize the zone button mode select."""
        super().__init__(coordinator, zone, "button_mode")
        self._attr_options = list(ZONE_BUTTON_MODES.values())
        self._attr_icon = "mdi:gesture-tap-button"

    @property
    def current_option(self) -> str | None:
        """Return the selected option."""
        mode = self.coordinator.data.get(f"zone_{self._zone}_button_mode")
        if mode is not None:
            return ZONE_BUTTON_MODES.get(mode, "boost")
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        # Find the mode number for the option
        mode = None
        for mode_num, mode_name in ZONE_BUTTON_MODES.items():
            if mode_name == option:
                mode = mode_num
                break
                
        if mode is not None:
            address = 401 + (self._zone - 1) * 10  # Button mode register address
            success = await self.coordinator.async_write_register(address, mode)
            if not success:
                _LOGGER.error("Failed to set zone %d button mode to %s", self._zone, option)


class JablotronFuturaZoneButtonTimerNumber(JablotronFuturaZoneBaseEntity, NumberEntity):
    """Zone button timer number for Jablotron Futura."""

    def __init__(self, coordinator: JablotronFuturaCoordinator, zone: int) -> None:
        """Initialize the zone button timer number."""
        super().__init__(coordinator, zone, "button_timer")
        self._attr_mode = NumberMode.BOX
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

    async def async_set_native_value(self, value: float) -> None:
        """Set the timer value."""
        int_value = int(value)
        address = 402 + (self._zone - 1) * 10  # Button timer register address
        success = await self.coordinator.async_write_register(address, int_value)
        if not success:
            _LOGGER.error("Failed to set zone %d button timer to %d", self._zone, int_value)


class JablotronFuturaZoneButtonActiveSwitch(JablotronFuturaZoneBaseEntity, SwitchEntity):
    """Zone button active switch for Jablotron Futura."""

    def __init__(self, coordinator: JablotronFuturaCoordinator, zone: int) -> None:
        """Initialize the zone button active switch."""
        super().__init__(coordinator, zone, "button_active")
        self._attr_icon = "mdi:gesture-tap-button"

    @property
    def is_on(self) -> bool | None:
        """Return true if the button is active."""
        value = self.coordinator.data.get(f"zone_{self._zone}_button_active")
        return bool(value) if value is not None else None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the button on."""
        address = 403 + (self._zone - 1) * 10  # Button active register address
        success = await self.coordinator.async_write_register(address, 1)
        if not success:
            _LOGGER.error("Failed to activate zone %d button", self._zone)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the button off."""
        address = 403 + (self._zone - 1) * 10  # Button active register address
        success = await self.coordinator.async_write_register(address, 0)
        if not success:
            _LOGGER.error("Failed to deactivate zone %d button", self._zone)
