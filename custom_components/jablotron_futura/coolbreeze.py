"""Support for Jablotron Futura CoolBreeze climate control."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import JablotronFuturaCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Jablotron Futura CoolBreeze entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Only create CoolBreeze entities if CoolBreeze is supported
    coolbreeze_supported = coordinator.data.get("config_coolbreeze_supported", False)
    if not coolbreeze_supported:
        _LOGGER.debug("CoolBreeze not supported, skipping CoolBreeze entities")
        return

    entities = [
        JablotronFuturaCoolBreezeClimate(coordinator),
        JablotronFuturaCoolBreezeOutputSensor(coordinator),
        JablotronFuturaCoolBreezeAutoPrioritySwitch(coordinator),
    ]

    async_add_entities(entities)


class JablotronFuturaCoolBreezeBase(CoordinatorEntity):
    """Base class for CoolBreeze entities."""

    def __init__(
        self,
        coordinator: JablotronFuturaCoordinator,
        entity_type: str,
    ) -> None:
        """Initialize the CoolBreeze entity."""
        super().__init__(coordinator)
        self._entity_type = entity_type
        
        self._attr_unique_id = f"{coordinator.host}_coolbreeze_{entity_type}"
        self._attr_name = f"CoolBreeze {entity_type.replace('_', ' ').title()}"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data.get("config_coolbreeze_supported", False)
            and not self.coordinator.data.get("error_coolbreeze_comm_error", False)
        )


class JablotronFuturaCoolBreezeClimate(JablotronFuturaCoolBreezeBase, ClimateEntity):
    """CoolBreeze climate entity for Jablotron Futura."""

    def __init__(self, coordinator: JablotronFuturaCoordinator) -> None:
        """Initialize the CoolBreeze climate entity."""
        super().__init__(coordinator, "climate")
        
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_icon = "mdi:heat-pump"
        
        # Supported features
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE |
            ClimateEntityFeature.TURN_ON |
            ClimateEntityFeature.TURN_OFF
        )
        
        # HVAC modes - CoolBreeze specific
        self._attr_hvac_modes = [
            HVACMode.OFF,
            HVACMode.HEAT,
            HVACMode.COOL,
            HVACMode.AUTO,
        ]
        
        # Temperature limits
        self._attr_min_temp = 10.0
        self._attr_max_temp = 35.0
        self._attr_target_temperature_step = 0.1

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        # Use supply air temperature as current temperature for CoolBreeze
        temp = self.coordinator.data.get("temp_fresh")
        return float(temp) if temp is not None else None

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        temp = self.coordinator.data.get("temp_setpoint")
        return float(temp) if temp is not None else None

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return current operation mode."""
        cooling_enabled = self.coordinator.data.get("cooling_enable", False)
        heating_enabled = self.coordinator.data.get("heating_enable", False)
        device_on = self.coordinator.data.get("mode_device_on", False)
        
        if not device_on:
            return HVACMode.OFF
        elif cooling_enabled and heating_enabled:
            return HVACMode.AUTO
        elif cooling_enabled:
            return HVACMode.COOL
        elif heating_enabled:
            return HVACMode.HEAT
        else:
            return HVACMode.OFF

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return the current running hvac operation."""
        if not self.coordinator.data.get("mode_device_on", False):
            return HVACAction.OFF
            
        # Check if CoolBreeze is actively heating or cooling
        heating_power = self.coordinator.data.get("heating_power", 0)
        supply_temp = self.coordinator.data.get("temp_fresh")
        outdoor_temp = self.coordinator.data.get("temp_ambient")
        
        if heating_power > 0:
            return HVACAction.HEATING
        elif supply_temp and outdoor_temp and supply_temp < outdoor_temp:
            return HVACAction.COOLING
        else:
            return HVACAction.IDLE

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
            
        # Convert to register format (0.1°C)
        temp_value = int(temperature * 10)
        
        success = await self.coordinator.async_write_register(10, temp_value)
        if not success:
            _LOGGER.error("Failed to set CoolBreeze target temperature to %s°C", temperature)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVACMode.OFF:
            # Turn off both heating and cooling
            await self._set_heating_cooling(False, False)
        elif hvac_mode == HVACMode.HEAT:
            # Enable heating, disable cooling
            await self._set_heating_cooling(True, False)
        elif hvac_mode == HVACMode.COOL:
            # Enable cooling, disable heating
            await self._set_heating_cooling(False, True)
        elif hvac_mode == HVACMode.AUTO:
            # Enable both heating and cooling
            await self._set_heating_cooling(True, True)

    async def _set_heating_cooling(self, heating: bool, cooling: bool) -> None:
        """Set heating and cooling enable states."""
        heating_success = await self.coordinator.async_write_register(15, int(heating))
        cooling_success = await self.coordinator.async_write_register(16, int(cooling))
        
        if not heating_success:
            _LOGGER.error("Failed to set CoolBreeze heating to %s", heating)
        if not cooling_success:
            _LOGGER.error("Failed to set CoolBreeze cooling to %s", cooling)


class JablotronFuturaCoolBreezeOutputSensor(JablotronFuturaCoolBreezeBase, SensorEntity):
    """CoolBreeze output percentage sensor for Jablotron Futura."""

    def __init__(self, coordinator: JablotronFuturaCoordinator) -> None:
        """Initialize the CoolBreeze output sensor."""
        super().__init__(coordinator, "output")
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_icon = "mdi:heat-pump"

    @property
    def native_value(self) -> float | None:
        """Return the CoolBreeze output percentage."""
        # This would need to be read from a specific CoolBreeze register
        # For now, we'll estimate based on heating power vs max power
        heating_power = self.coordinator.data.get("heating_power", 0)
        if heating_power is not None and heating_power > 0:
            # Assuming max heating power is around 2000W (this should be configurable)
            max_power = 2000
            return min(100.0, (heating_power / max_power) * 100)
        return 0.0

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        return {
            "heating_power": self.coordinator.data.get("heating_power"),
            "cooling_available": self.coordinator.data.get("config_coolbreeze_cooling_available"),
            "heating_available": self.coordinator.data.get("config_coolbreeze_heating_available"),
        }


class JablotronFuturaCoolBreezeAutoPrioritySwitch(JablotronFuturaCoolBreezeBase, SwitchEntity):
    """CoolBreeze auto priority control switch for Jablotron Futura."""

    def __init__(self, coordinator: JablotronFuturaCoordinator) -> None:
        """Initialize the CoolBreeze auto priority switch."""
        super().__init__(coordinator, "auto_priority")
        self._attr_name = "CoolBreeze Auto Priority (CO2 vs Temperature)"
        self._attr_icon = "mdi:auto-mode"

    @property
    def is_on(self) -> bool | None:
        """Return true if CO2 priority is enabled (vs temperature priority)."""
        value = self.coordinator.data.get("vb_coolbreeze_priority")
        return bool(value) if value is not None else None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        priority = self.coordinator.data.get("vb_coolbreeze_priority", 0)
        return {
            "priority_mode": "CO2" if priority else "Temperature",
            "description": "When CoolBreeze is active, AUTO mode in zone ventilation is controlled by CO2 if ON, Temperature if OFF"
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on CO2 priority."""
        success = await self.coordinator.async_write_register(20, 1)
        if not success:
            _LOGGER.error("Failed to enable CoolBreeze CO2 priority")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off CO2 priority (use temperature priority)."""
        success = await self.coordinator.async_write_register(20, 0)
        if not success:
            _LOGGER.error("Failed to disable CoolBreeze CO2 priority")
