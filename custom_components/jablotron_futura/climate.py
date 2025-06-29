
# =============================================================================
# climate.py - Climate Entity
# =============================================================================

"""Support for Jablotron Futura climate entity."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
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
    """Set up the Jablotron Futura climate entity."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        JablotronFuturaClimate(coordinator),
    ]

    # Add CoolBreeze climate entity if CoolBreeze is supported
    coolbreeze_supported = coordinator.data.get("config_coolbreeze_supported", False)
    if coolbreeze_supported:
        entities.append(JablotronFuturaCoolBreezeClimate(coordinator))

    async_add_entities(entities)


class JablotronFuturaClimate(CoordinatorEntity, ClimateEntity):
    """Climate entity for Jablotron Futura."""

    def __init__(self, coordinator: JablotronFuturaCoordinator) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)
        
        self._attr_unique_id = f"{coordinator.host}_climate"
        self._attr_name = "Futura Climate"
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_icon = "mdi:thermostat"
        
        # Supported features
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE |
            ClimateEntityFeature.FAN_MODE
        )
        
        # HVAC modes
        self._attr_hvac_modes = [
            HVACMode.OFF,
            HVACMode.FAN_ONLY,
            HVACMode.HEAT,
            HVACMode.COOL,
            HVACMode.AUTO,
        ]
        
        # Fan modes (ventilation levels)
        self._attr_fan_modes = [
            "level_1",
            "level_2", 
            "level_3",
            "level_4",
            "level_5",
            "auto",
        ]
        
        # Temperature limits
        self._attr_min_temp = 10.0
        self._attr_max_temp = 30.0
        self._attr_target_temperature_step = 0.1

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        # Use supply air temperature as current temperature
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
        # Determine mode based on device status
        ventilation_level = self.coordinator.data.get("ventilation_level", 0)
        heating_enabled = self.coordinator.data.get("heating_enable", False)
        cooling_enabled = self.coordinator.data.get("cooling_enable", False)
        device_on = self.coordinator.data.get("mode_device_on", False)
        
        if not device_on or ventilation_level == 0:
            return HVACMode.OFF
        elif heating_enabled and cooling_enabled:
            return HVACMode.AUTO
        elif heating_enabled:
            return HVACMode.HEAT
        elif cooling_enabled:
            return HVACMode.COOL
        else:
            return HVACMode.FAN_ONLY

    @property
    def fan_mode(self) -> str | None:
        """Return the fan setting."""
        level = self.coordinator.data.get("ventilation_level")
        if level == 0:
            return None
        elif level == 6:
            return "auto"
        else:
            return f"level_{level}"

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
            
        # Convert to register format (0.1°C)
        temp_value = int(temperature * 10)
        config = HOLDING_REGISTERS["temp_setpoint"]
        address = config["address"]
        
        success = await self.coordinator.async_write_register(address, temp_value)
        if not success:
            _LOGGER.error("Failed to set target temperature to %s°C", temperature)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVACMode.OFF:
            # Turn off ventilation
            address = HOLDING_REGISTERS["ventilation_level"]["address"]
            await self.coordinator.async_write_register(address, 0)
        elif hvac_mode == HVACMode.FAN_ONLY:
            # Enable ventilation, disable heating/cooling
            await self._set_heating_cooling(False, False)
            # Set to level 1 if currently off
            if self.coordinator.data.get("ventilation_level", 0) == 0:
                address = HOLDING_REGISTERS["ventilation_level"]["address"]
                await self.coordinator.async_write_register(address, 1)
        elif hvac_mode == HVACMode.HEAT:
            # Enable heating, disable cooling
            await self._set_heating_cooling(True, False)
        elif hvac_mode == HVACMode.COOL:
            # Enable cooling, disable heating
            await self._set_heating_cooling(False, True)
        elif hvac_mode == HVACMode.AUTO:
            # Enable both heating and cooling
            await self._set_heating_cooling(True, True)

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        level_map = {
            "level_1": 1,
            "level_2": 2,
            "level_3": 3,
            "level_4": 4,
            "level_5": 5,
            "auto": 6,
        }
        
        level = level_map.get(fan_mode)
        if level is not None:
            address = HOLDING_REGISTERS["ventilation_level"]["address"]
            success = await self.coordinator.async_write_register(address, level)
            if not success:
                _LOGGER.error("Failed to set fan mode to %s", fan_mode)

    async def _set_heating_cooling(self, heating: bool, cooling: bool) -> None:
        """Set heating and cooling enable states."""
        heating_addr = HOLDING_REGISTERS["heating_enable"]["address"]
        cooling_addr = HOLDING_REGISTERS["cooling_enable"]["address"]
        
        await self.coordinator.async_write_register(heating_addr, int(heating))
        await self.coordinator.async_write_register(cooling_addr, int(cooling))


class JablotronFuturaCoolBreezeClimate(CoordinatorEntity, ClimateEntity):
    """CoolBreeze climate entity for Jablotron Futura."""

    def __init__(self, coordinator: JablotronFuturaCoordinator) -> None:
        """Initialize the CoolBreeze climate entity."""
        super().__init__(coordinator)
        
        self._attr_unique_id = f"{coordinator.host}_coolbreeze_climate"
        self._attr_name = "CoolBreeze Climate"
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
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data.get("config_coolbreeze_supported", False)
            and not self.coordinator.data.get("error_coolbreeze_comm_error", False)
        )

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

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
            
        # Convert to register format (0.1°C)
        temp_value = int(temperature * 10)
        config = HOLDING_REGISTERS["temp_setpoint"]
        address = config["address"]
        
        success = await self.coordinator.async_write_register(address, temp_value)
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
        heating_addr = HOLDING_REGISTERS["heating_enable"]["address"]
        cooling_addr = HOLDING_REGISTERS["cooling_enable"]["address"]
        
        heating_success = await self.coordinator.async_write_register(heating_addr, int(heating))
        cooling_success = await self.coordinator.async_write_register(cooling_addr, int(cooling))
        
        if not heating_success:
            _LOGGER.error("Failed to set CoolBreeze heating to %s", heating)
        if not cooling_success:
            _LOGGER.error("Failed to set CoolBreeze cooling to %s", cooling)
