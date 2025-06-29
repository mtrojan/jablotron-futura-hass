# =============================================================================
# binary_sensor.py - Binary Sensor Entities
# =============================================================================

"""Support for Jablotron Futura binary sensors."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    MODE_BITS,
    ERROR_BITS,
    WARNING_BITS,
    CONFIG_BITS,
    ZONE_BITS,
)
from .coordinator import JablotronFuturaCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Jablotron Futura binary sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []

    # Mode status sensors
    for bit, name in MODE_BITS.items():
        entities.append(JablotronFuturaModeBinarySensor(coordinator, bit, name))

    # Error sensors
    for bit, name in ERROR_BITS.items():
        entities.append(JablotronFuturaErrorBinarySensor(coordinator, bit, name))

    # Warning sensors
    for bit, name in WARNING_BITS.items():
        entities.append(JablotronFuturaWarningBinarySensor(coordinator, bit, name))

    # Configuration sensors (capabilities)
    for bit, name in CONFIG_BITS.items():
        entities.append(JablotronFuturaConfigBinarySensor(coordinator, bit, name))

    # Zone presence sensors
    for bit, name in ZONE_BITS.items():
        entities.append(JablotronFuturaZoneBinarySensor(coordinator, bit, name))

    # Zone button presence sensors
    for zone in range(1, 9):
        entities.append(JablotronFuturaZoneButtonPresenceSensor(coordinator, zone))
        entities.append(JablotronFuturaZoneButtonActiveSensor(coordinator, zone))
        entities.append(JablotronFuturaSensorPresenceSensor(coordinator, zone))

    async_add_entities(entities)


class JablotronFuturaBaseBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Base class for Jablotron Futura binary sensors."""

    def __init__(
        self,
        coordinator: JablotronFuturaCoordinator,
        sensor_key: str,
        name: str,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        
        self._attr_unique_id = f"{coordinator.host}_{sensor_key}"
        self._attr_name = name


class JablotronFuturaModeBinarySensor(JablotronFuturaBaseBinarySensor):
    """Mode status binary sensor for Jablotron Futura."""

    def __init__(
        self,
        coordinator: JablotronFuturaCoordinator,
        bit: int,
        name: str,
    ) -> None:
        """Initialize the mode sensor."""
        super().__init__(coordinator, f"mode_{name}", f"Mode: {name.replace('_', ' ').title()}")
        self._bit = bit
        self._attr_icon = "mdi:information"

    @property
    def is_on(self) -> bool | None:
        """Return true if the mode is active."""
        return self.coordinator.data.get(f"mode_{MODE_BITS[self._bit]}", False)


class JablotronFuturaErrorBinarySensor(JablotronFuturaBaseBinarySensor):
    """Error binary sensor for Jablotron Futura."""

    def __init__(
        self,
        coordinator: JablotronFuturaCoordinator,
        bit: int,
        name: str,
    ) -> None:
        """Initialize the error sensor."""
        super().__init__(coordinator, f"error_{name}", f"Error: {name.replace('_', ' ').title()}")
        self._bit = bit
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM
        self._attr_icon = "mdi:alert"

    @property
    def is_on(self) -> bool | None:
        """Return true if the error is active."""
        return self.coordinator.data.get(f"error_{ERROR_BITS[self._bit]}", False)


class JablotronFuturaWarningBinarySensor(JablotronFuturaBaseBinarySensor):
    """Warning binary sensor for Jablotron Futura."""

    def __init__(
        self,
        coordinator: JablotronFuturaCoordinator,
        bit: int,
        name: str,
    ) -> None:
        """Initialize the warning sensor."""
        super().__init__(coordinator, f"warning_{name}", f"Warning: {name.replace('_', ' ').title()}")
        self._bit = bit
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM
        self._attr_icon = "mdi:alert-outline"

    @property
    def is_on(self) -> bool | None:
        """Return true if the warning is active."""
        return self.coordinator.data.get(f"warning_{WARNING_BITS[self._bit]}", False)


class JablotronFuturaConfigBinarySensor(JablotronFuturaBaseBinarySensor):
    """Configuration capability binary sensor for Jablotron Futura."""

    def __init__(
        self,
        coordinator: JablotronFuturaCoordinator,
        bit: int,
        name: str,
    ) -> None:
        """Initialize the config sensor."""
        super().__init__(coordinator, f"config_{name}", f"Capability: {name.replace('_', ' ').title()}")
        self._bit = bit
        self._attr_icon = "mdi:feature-search"
        self._attr_entity_category = "diagnostic"

    @property
    def is_on(self) -> bool | None:
        """Return true if the capability is available."""
        device_config = self.coordinator.data.get("device_config", 0)
        return bool(device_config & (1 << self._bit)) if device_config is not None else None


class JablotronFuturaZoneBinarySensor(JablotronFuturaBaseBinarySensor):
    """Zone presence binary sensor for Jablotron Futura."""

    def __init__(
        self,
        coordinator: JablotronFuturaCoordinator,
        bit: int,
        name: str,
    ) -> None:
        """Initialize the zone sensor."""
        super().__init__(coordinator, f"zone_{name}", f"Zone: {name.replace('_', ' ').title()}")
        self._bit = bit
        self._attr_icon = "mdi:home-outline"
        self._attr_entity_category = "diagnostic"

    @property
    def is_on(self) -> bool | None:
        """Return true if the zone is configured."""
        zone_config = self.coordinator.data.get("vzv_identify", 0)
        return bool(zone_config & (1 << self._bit)) if zone_config is not None else None


class JablotronFuturaZoneButtonPresenceSensor(JablotronFuturaBaseBinarySensor):
    """Zone button presence binary sensor for Jablotron Futura."""

    def __init__(
        self,
        coordinator: JablotronFuturaCoordinator,
        zone: int,
    ) -> None:
        """Initialize the zone button presence sensor."""
        super().__init__(coordinator, f"zone_{zone}_button_present", f"Zone {zone} Button Present")
        self._zone = zone
        self._attr_icon = "mdi:gesture-tap-button"
        self._attr_entity_category = "diagnostic"

    @property
    def is_on(self) -> bool | None:
        """Return true if the zone button is present."""
        return bool(self.coordinator.data.get(f"zone_{self._zone}_button_present", False))


class JablotronFuturaZoneButtonActiveSensor(JablotronFuturaBaseBinarySensor):
    """Zone button active binary sensor for Jablotron Futura."""

    def __init__(
        self,
        coordinator: JablotronFuturaCoordinator,
        zone: int,
    ) -> None:
        """Initialize the zone button active sensor."""
        super().__init__(coordinator, f"zone_{zone}_button_active", f"Zone {zone} Button Active")
        self._zone = zone
        self._attr_icon = "mdi:gesture-tap-button"

    @property
    def is_on(self) -> bool | None:
        """Return true if the zone button is active."""
        return bool(self.coordinator.data.get(f"zone_{self._zone}_button_active", False))


class JablotronFuturaSensorPresenceSensor(JablotronFuturaBaseBinarySensor):
    """Zone sensor presence binary sensor for Jablotron Futura."""

    def __init__(
        self,
        coordinator: JablotronFuturaCoordinator,
        zone: int,
    ) -> None:
        """Initialize the zone sensor presence sensor."""
        super().__init__(coordinator, f"zone_{zone}_sensors_present", f"Zone {zone} Sensors Present")
        self._zone = zone
        self._attr_icon = "mdi:sensor"
        self._attr_entity_category = "diagnostic"

    @property
    def is_on(self) -> bool | None:
        """Return true if the zone sensors are present."""
        return bool(self.coordinator.data.get(f"zone_{self._zone}_sensors_present", False))

