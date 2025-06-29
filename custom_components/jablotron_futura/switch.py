
# =============================================================================
# switch.py - Switch Entities  
# =============================================================================

"""Support for Jablotron Futura switch entities."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
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
    """Set up the Jablotron Futura switch entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Boolean control switches
    switch_registers = [
        "time_program_enable",
        "antiradon_enable", 
        "bypass_enable",
        "heating_enable",
        "cooling_enable",
        "comfort_enable",
    ]

    entities = []
    for register_key in switch_registers:
        entities.append(JablotronFuturaSwitch(coordinator, register_key))

    # Add zone button active switches if VarioBreeze is supported
    variobreeze_supported = coordinator.data.get("config_variobreeze_supported", False)
    if variobreeze_supported:
        for zone in range(1, 9):
            zone_button_present = coordinator.data.get(f"zone_{zone}_button_present", False)
            if zone_button_present:
                entities.append(JablotronFuturaZoneButtonActiveSwitch(coordinator, zone))

    # Add CoolBreeze/VarioBreeze configuration switches
    coolbreeze_supported = coordinator.data.get("config_coolbreeze_supported", False)
    if coolbreeze_supported and variobreeze_supported:
        entities.extend([
            JablotronFuturaCoolBreezeAutoPrioritySwitch(coordinator),
            JablotronFuturaKitchenHoodModeSwitch(coordinator),
        ])

    async_add_entities(entities)


class JablotronFuturaSwitch(CoordinatorEntity, SwitchEntity):
    """Switch entity for Jablotron Futura."""

    def __init__(
        self,
        coordinator: JablotronFuturaCoordinator,
        register_key: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._register_key = register_key
        self._config = HOLDING_REGISTERS.get(register_key, {})
        
        self._attr_unique_id = f"{coordinator.host}_{register_key}"
        self._attr_name = self._config.get("name", register_key)
        
        # Set appropriate icons
        icon_map = {
            "time_program_enable": "mdi:calendar-clock",
            "antiradon_enable": "mdi:radioactive",
            "bypass_enable": "mdi:valve", 
            "heating_enable": "mdi:radiator",
            "cooling_enable": "mdi:snowflake",
            "comfort_enable": "mdi:thermostat",
        }
        self._attr_icon = icon_map.get(register_key, "mdi:toggle-switch")

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        value = self.coordinator.data.get(self._register_key)
        return bool(value) if value is not None else None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        address = self._config["address"]
        success = await self.coordinator.async_write_register(address, 1)
        if not success:
            _LOGGER.error("Failed to turn on %s", self._attr_name)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off.""" 
        address = self._config["address"]
        success = await self.coordinator.async_write_register(address, 0)
        if not success:
            _LOGGER.error("Failed to turn off %s", self._attr_name)


# =============================================================================
# Zone and CoolBreeze Switch Classes
# =============================================================================

class JablotronFuturaZoneButtonActiveSwitch(CoordinatorEntity, SwitchEntity):
    """Zone button active switch for Jablotron Futura."""

    def __init__(
        self,
        coordinator: JablotronFuturaCoordinator,
        zone: int,
    ) -> None:
        """Initialize the zone button active switch."""
        super().__init__(coordinator)
        self._zone = zone
        
        self._attr_unique_id = f"{coordinator.host}_zone_{zone}_button_active"
        self._attr_name = f"Zone {zone} Button Active"
        self._attr_icon = "mdi:gesture-tap-button"

    @property
    def is_on(self) -> bool | None:
        """Return true if the button is active."""
        value = self.coordinator.data.get(f"zone_{self._zone}_button_active")
        return bool(value) if value is not None else None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data.get(f"zone_{self._zone}_button_present", False)
        )

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


class JablotronFuturaCoolBreezeAutoPrioritySwitch(CoordinatorEntity, SwitchEntity):
    """CoolBreeze auto priority control switch for Jablotron Futura."""

    def __init__(self, coordinator: JablotronFuturaCoordinator) -> None:
        """Initialize the CoolBreeze auto priority switch."""
        super().__init__(coordinator)
        
        self._attr_unique_id = f"{coordinator.host}_coolbreeze_auto_priority"
        self._attr_name = "CoolBreeze Auto Priority (CO2 vs Temperature)"
        self._attr_icon = "mdi:auto-mode"

    @property
    def is_on(self) -> bool | None:
        """Return true if CO2 priority is enabled (vs temperature priority)."""
        value = self.coordinator.data.get("vb_coolbreeze_priority")
        return bool(value) if value is not None else None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data.get("config_coolbreeze_supported", False)
            and self.coordinator.data.get("config_variobreeze_supported", False)
        )

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


class JablotronFuturaKitchenHoodModeSwitch(CoordinatorEntity, SwitchEntity):
    """Kitchen hood normally open switch for Jablotron Futura."""

    def __init__(self, coordinator: JablotronFuturaCoordinator) -> None:
        """Initialize the kitchen hood mode switch."""
        super().__init__(coordinator)
        
        self._attr_unique_id = f"{coordinator.host}_kitchen_hood_normally_open"
        self._attr_name = "Kitchen Hood Normally Open"
        self._attr_icon = "mdi:stove"

    @property
    def is_on(self) -> bool | None:
        """Return true if kitchen hood is normally open."""
        value = self.coordinator.data.get("vb_kitchen_hood_normal")
        return bool(value) if value is not None else None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data.get("config_variobreeze_supported", False)
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        mode = self.coordinator.data.get("vb_kitchen_hood_normal", 0)
        return {
            "mode": "Normally Open" if mode else "Normally Closed",
            "description": "Kitchen hood exhaust damper default position"
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Set kitchen hood to normally open."""
        success = await self.coordinator.async_write_register(21, 1)
        if not success:
            _LOGGER.error("Failed to set kitchen hood to normally open")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Set kitchen hood to normally closed."""
        success = await self.coordinator.async_write_register(21, 0)
        if not success:
            _LOGGER.error("Failed to set kitchen hood to normally closed")
