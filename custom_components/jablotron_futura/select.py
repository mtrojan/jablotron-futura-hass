# =============================================================================
# select.py - Select Entities
# =============================================================================

"""Support for Jablotron Futura select entities."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, HOLDING_REGISTERS, VENTILATION_LEVELS, ZONE_BUTTON_MODES
from .coordinator import JablotronFuturaCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Jablotron Futura select entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        JablotronFuturaVentilationLevelSelect(coordinator),
    ]

    # Add zone button mode selects if VarioBreeze is supported
    variobreeze_supported = coordinator.data.get("config_variobreeze_supported", False)
    if variobreeze_supported:
        for zone in range(1, 9):
            zone_button_present = coordinator.data.get(f"zone_{zone}_button_present", False)
            if zone_button_present:
                entities.append(JablotronFuturaZoneButtonModeSelect(coordinator, zone))

    async_add_entities(entities)


class JablotronFuturaBaseSelect(CoordinatorEntity, SelectEntity):
    """Base class for Jablotron Futura select entities."""

    def __init__(
        self,
        coordinator: JablotronFuturaCoordinator,
        register_key: str,
    ) -> None:
        """Initialize the select."""
        super().__init__(coordinator)
        self._register_key = register_key
        self._config = HOLDING_REGISTERS.get(register_key, {})
        
        self._attr_unique_id = f"{coordinator.host}_{register_key}"
        self._attr_name = self._config.get("name", register_key)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        # This will be implemented by subclasses
        raise NotImplementedError


class JablotronFuturaVentilationLevelSelect(JablotronFuturaBaseSelect):
    """Ventilation level select for Jablotron Futura."""

    def __init__(self, coordinator: JablotronFuturaCoordinator) -> None:
        """Initialize the select."""
        super().__init__(coordinator, "ventilation_level")
        self._attr_options = list(VENTILATION_LEVELS.values())
        self._attr_icon = "mdi:fan"

    @property
    def current_option(self) -> str | None:
        """Return the selected option."""
        level = self.coordinator.data.get("ventilation_level")
        if level is not None:
            return VENTILATION_LEVELS.get(level, "off")
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        # Find the level number for the option
        level = None
        for level_num, level_name in VENTILATION_LEVELS.items():
            if level_name == option:
                level = level_num
                break
                
        if level is not None:
            address = self._config["address"]
            success = await self.coordinator.async_write_register(address, level)
            if not success:
                _LOGGER.error("Failed to set ventilation level to %s", option)


class JablotronFuturaZoneButtonModeSelect(JablotronFuturaBaseSelect):
    """Zone button mode select for Jablotron Futura."""

    def __init__(self, coordinator: JablotronFuturaCoordinator, zone: int) -> None:
        """Initialize the zone button mode select."""
        super().__init__(coordinator, f"zone_{zone}_button_mode")
        self._zone = zone
        self._attr_name = f"Zone {zone} Button Mode"
        self._attr_options = list(ZONE_BUTTON_MODES.values())
        self._attr_icon = "mdi:gesture-tap-button"

    @property
    def current_option(self) -> str | None:
        """Return the selected option."""
        mode = self.coordinator.data.get(f"zone_{self._zone}_button_mode")
        if mode is not None:
            return ZONE_BUTTON_MODES.get(mode, "boost")
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data.get(f"zone_{self._zone}_button_present", False)
        )

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
