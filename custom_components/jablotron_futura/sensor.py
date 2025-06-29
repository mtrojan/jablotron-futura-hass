"""Support for Jablotron Futura sensors."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    UnitOfElectricPotential,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfVolumetricFlowRate,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, INPUT_REGISTERS, DEVICE_VARIANTS
from .coordinator import JablotronFuturaCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Jablotron Futura sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []

    # Temperature sensors
    temp_sensors = [
        "temp_ambient",
        "temp_fresh", 
        "temp_indoor",
        "temp_waste",
        "temp_external_ntc",
    ]

    for sensor_key in temp_sensors:
        entities.append(JablotronFuturaTemperatureSensor(coordinator, sensor_key))

    # Humidity sensors
    humidity_sensors = [
        "humidity_ambient",
        "humidity_fresh",
        "humidity_indoor", 
        "humidity_waste",
    ]

    for sensor_key in humidity_sensors:
        entities.append(JablotronFuturaHumiditySensor(coordinator, sensor_key))

    # Power sensors
    power_sensors = [
        "power_consumption",
        "heat_recovery",
        "heating_power",
    ]

    for sensor_key in power_sensors:
        entities.append(JablotronFuturaPowerSensor(coordinator, sensor_key))

    # Percentage sensors
    percentage_sensors = [
        "filter_wear_level",
        "fan_supply_pwm",
        "fan_exhaust_pwm",
    ]

    for sensor_key in percentage_sensors:
        entities.append(JablotronFuturaPercentageSensor(coordinator, sensor_key))

    # Flow rate sensor
    entities.append(JablotronFuturaFlowRateSensor(coordinator, "air_flow"))

    # RPM sensors
    rpm_sensors = [
        "fan_supply_rpm",
        "fan_exhaust_rpm",
    ]

    for sensor_key in rpm_sensors:
        entities.append(JablotronFuturaRpmSensor(coordinator, sensor_key))

    # Voltage sensors
    voltage_sensors = [
        "voltage_uin1",
        "voltage_uin2", 
        "battery_voltage",
    ]

    for sensor_key in voltage_sensors:
        entities.append(JablotronFuturaVoltageSensor(coordinator, sensor_key))

    # Device info sensors
    entities.extend([
        JablotronFuturaDeviceVariantSensor(coordinator),
        JablotronFuturaSerialNumberSensor(coordinator),
        JablotronFuturaVersionSensor(coordinator, "hw_version", "Hardware Version"),
        JablotronFuturaVersionSensor(coordinator, "fw_version", "Firmware Version"),
        JablotronFuturaVersionSensor(coordinator, "regmap_version", "Register Map Version"),
    ])

    # Zone sensor entities (only if VarioBreeze is supported)
    variobreeze_supported = coordinator.data.get("config_variobreeze_supported", False)
    if variobreeze_supported:
        for zone in range(1, 9):
            # Only add zone sensors if zone sensors are present
            zone_sensors_present = coordinator.data.get(f"zone_{zone}_sensors_present", False)
            if zone_sensors_present:
                entities.extend([
                    JablotronFuturaZoneTemperatureSensor(coordinator, zone),
                    JablotronFuturaZoneHumiditySensor(coordinator, zone),
                    JablotronFuturaZoneCO2Sensor(coordinator, zone),
                    JablotronFuturaZoneFloorTemperatureSensor(coordinator, zone),
                ])

    async_add_entities(entities)


class JablotronFuturaBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for Jablotron Futura sensors."""

    def __init__(
        self,
        coordinator: JablotronFuturaCoordinator,
        sensor_key: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._config = INPUT_REGISTERS.get(sensor_key, {})
        
        self._attr_unique_id = f"{coordinator.host}_{sensor_key}"
        self._attr_name = self._config.get("name", sensor_key)
        
        device_info = self._get_device_info()
        if device_info:
            self._attr_device_info = device_info

    def _get_device_info(self) -> dict[str, Any] | None:
        """Return device info."""
        serial_number = self.coordinator.data.get("serial_number")
        device_variant = self.coordinator.data.get("device_variant")
        
        if serial_number is None:
            return None
            
        model = DEVICE_VARIANTS.get(device_variant, f"Futura (variant {device_variant})")
        
        return {
            "identifiers": {(DOMAIN, str(serial_number))},
            "name": "Jablotron Futura",
            "manufacturer": "Jablotron Living Technology",
            "model": model,
            "sw_version": self.coordinator.data.get("fw_version"),
        }

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        value = self.coordinator.data.get(self._sensor_key)
        
        # Handle special cases
        if self._sensor_key == "temp_external_ntc" and value == -99:
            return None  # NTC not connected
            
        return value

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data.get(self._sensor_key) is not None
        )


class JablotronFuturaTemperatureSensor(JablotronFuturaBaseSensor):
    """Temperature sensor for Jablotron Futura."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS


class JablotronFuturaHumiditySensor(JablotronFuturaBaseSensor):
    """Humidity sensor for Jablotron Futura."""

    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE


class JablotronFuturaPowerSensor(JablotronFuturaBaseSensor):
    """Power sensor for Jablotron Futura."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT


class JablotronFuturaPercentageSensor(JablotronFuturaBaseSensor):
    """Percentage sensor for Jablotron Futura."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE


class JablotronFuturaFlowRateSensor(JablotronFuturaBaseSensor):
    """Flow rate sensor for Jablotron Futura."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfVolumetricFlowRate.CUBIC_METERS_PER_HOUR
    _attr_icon = "mdi:fan"


class JablotronFuturaRpmSensor(JablotronFuturaBaseSensor):
    """RPM sensor for Jablotron Futura."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "rpm"
    _attr_icon = "mdi:fan"


class JablotronFuturaVoltageSensor(JablotronFuturaBaseSensor):
    """Voltage sensor for Jablotron Futura."""

    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT


class JablotronFuturaDeviceVariantSensor(JablotronFuturaBaseSensor):
    """Device variant sensor for Jablotron Futura."""

    def __init__(self, coordinator: JablotronFuturaCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "device_variant")
        self._attr_name = "Device Variant"
        self._attr_icon = "mdi:information"

    @property
    def native_value(self) -> str | None:
        """Return the device variant name."""
        variant = self.coordinator.data.get("device_variant")
        if variant is not None:
            return DEVICE_VARIANTS.get(variant, f"Unknown ({variant})")
        return None


class JablotronFuturaSerialNumberSensor(JablotronFuturaBaseSensor):
    """Serial number sensor for Jablotron Futura."""

    def __init__(self, coordinator: JablotronFuturaCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "serial_number")
        self._attr_name = "Serial Number"
        self._attr_icon = "mdi:identifier"


class JablotronFuturaVersionSensor(JablotronFuturaBaseSensor):
    """Version sensor for Jablotron Futura."""

    def __init__(
        self, 
        coordinator: JablotronFuturaCoordinator,
        version_key: str,
        name: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, version_key)
        self._attr_name = name
        self._attr_icon = "mdi:information"

    @property
    def native_value(self) -> str | None:
        """Return the version as formatted string."""
        value = self.coordinator.data.get(self._sensor_key)
        if value is not None:
            # Format as version string (e.g., 1.2.3.4)
            return f"{(value >> 24) & 0xFF}.{(value >> 16) & 0xFF}.{(value >> 8) & 0xFF}.{value & 0xFF}"
        return None


# =============================================================================
# Zone Sensor Classes
# =============================================================================

class JablotronFuturaZoneBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for zone sensors."""

    def __init__(
        self,
        coordinator: JablotronFuturaCoordinator,
        zone: int,
        sensor_type: str,
    ) -> None:
        """Initialize the zone sensor."""
        super().__init__(coordinator)
        self._zone = zone
        self._sensor_type = sensor_type
        self._sensor_key = f"zone_{zone}_{sensor_type}"
        
        self._attr_unique_id = f"{coordinator.host}_zone_{zone}_{sensor_type}"
        self._attr_name = f"Zone {zone} {sensor_type.replace('_', ' ').title()}"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data.get(f"zone_{self._zone}_sensors_present", False)
            and self.coordinator.data.get(self._sensor_key) is not None
        )

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._sensor_key)


class JablotronFuturaZoneTemperatureSensor(JablotronFuturaZoneBaseSensor):
    """Zone temperature sensor for Jablotron Futura."""

    def __init__(self, coordinator: JablotronFuturaCoordinator, zone: int) -> None:
        """Initialize the zone temperature sensor."""
        super().__init__(coordinator, zone, "temperature")
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS


class JablotronFuturaZoneHumiditySensor(JablotronFuturaZoneBaseSensor):
    """Zone humidity sensor for Jablotron Futura."""

    def __init__(self, coordinator: JablotronFuturaCoordinator, zone: int) -> None:
        """Initialize the zone humidity sensor."""
        super().__init__(coordinator, zone, "humidity")
        self._attr_device_class = SensorDeviceClass.HUMIDITY
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = PERCENTAGE


class JablotronFuturaZoneCO2Sensor(JablotronFuturaZoneBaseSensor):
    """Zone CO2 sensor for Jablotron Futura."""

    def __init__(self, coordinator: JablotronFuturaCoordinator, zone: int) -> None:
        """Initialize the zone CO2 sensor."""
        super().__init__(coordinator, zone, "co2")
        self._attr_device_class = SensorDeviceClass.CARBON_DIOXIDE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = CONCENTRATION_PARTS_PER_MILLION


class JablotronFuturaZoneFloorTemperatureSensor(JablotronFuturaZoneBaseSensor):
    """Zone floor temperature sensor for Jablotron Futura."""

    def __init__(self, coordinator: JablotronFuturaCoordinator, zone: int) -> None:
        """Initialize the zone floor temperature sensor."""
        super().__init__(coordinator, zone, "floor_temperature")
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
