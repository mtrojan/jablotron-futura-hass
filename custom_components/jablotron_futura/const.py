# =============================================================================
# const.py - Konstanty a definice registrů
# =============================================================================

DOMAIN = "jablotron_futura"
DEFAULT_NAME = "Jablotron Futura"
DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 1

# Configuration constants
CONF_SLAVE_ID = "slave_id"

# Input Registry - Read Only
INPUT_REGISTERS = {
    # Device info
    "device_id": {"address": 0, "type": "uint16", "name": "Device ID"},
    "serial_number": {"address": 1, "type": "uint32", "name": "Serial Number"},
    "mac_address": {"address": 3, "type": "uint16", "count": 3, "name": "MAC Address"},
    "hw_version": {"address": 6, "type": "uint32", "name": "Hardware Version"},
    "fw_version": {"address": 8, "type": "uint32", "name": "Firmware Version"},
    "regmap_version": {"address": 12, "type": "uint32", "name": "Register Map Version"},
    "device_variant": {"address": 14, "type": "uint16", "name": "Device Variant"},
    "device_config": {"address": 15, "type": "uint16", "name": "Device Configuration"},
    
    # Status and mode
    "current_mode": {"address": 16, "type": "uint32", "name": "Current Mode"},
    "errors": {"address": 18, "type": "uint32", "name": "Errors"},
    "warnings": {"address": 20, "type": "uint32", "name": "Warnings"},
    
    # Temperatures (0.1°C)
    "temp_ambient": {"address": 30, "type": "int16", "scale": 0.1, "unit": "°C", "name": "Outdoor Air Temperature"},
    "temp_fresh": {"address": 31, "type": "int16", "scale": 0.1, "unit": "°C", "name": "Supply Air Temperature"},
    "temp_indoor": {"address": 32, "type": "int16", "scale": 0.1, "unit": "°C", "name": "Extract Air Temperature"},
    "temp_waste": {"address": 33, "type": "int16", "scale": 0.1, "unit": "°C", "name": "Exhaust Air Temperature"},
    "temp_external_ntc": {"address": 38, "type": "int16", "scale": 0.1, "unit": "°C", "name": "External NTC Temperature"},
    
    # Humidity (0.1%)
    "humidity_ambient": {"address": 34, "type": "int16", "scale": 0.1, "unit": "%", "name": "Outdoor Air Humidity"},
    "humidity_fresh": {"address": 35, "type": "int16", "scale": 0.1, "unit": "%", "name": "Supply Air Humidity"},
    "humidity_indoor": {"address": 36, "type": "int16", "scale": 0.1, "unit": "%", "name": "Extract Air Humidity"},
    "humidity_waste": {"address": 37, "type": "int16", "scale": 0.1, "unit": "%", "name": "Exhaust Air Humidity"},
    
    # Performance
    "filter_wear_level": {"address": 40, "type": "uint16", "unit": "%", "name": "Filter Wear Level"},
    "power_consumption": {"address": 41, "type": "uint16", "unit": "W", "name": "Power Consumption"},
    "heat_recovery": {"address": 42, "type": "uint16", "unit": "W", "name": "Heat Recovery"},
    "heating_power": {"address": 43, "type": "uint16", "unit": "W", "name": "Heating Power"},
    "air_flow": {"address": 44, "type": "uint16", "unit": "m³/h", "name": "Air Flow"},
    
    # Fans
    "fan_supply_pwm": {"address": 45, "type": "uint16", "unit": "%", "name": "Supply Fan PWM"},
    "fan_exhaust_pwm": {"address": 46, "type": "uint16", "unit": "%", "name": "Exhaust Fan PWM"},
    "fan_supply_rpm": {"address": 47, "type": "uint16", "unit": "rpm", "name": "Supply Fan RPM"},
    "fan_exhaust_rpm": {"address": 48, "type": "uint16", "unit": "rpm", "name": "Exhaust Fan RPM"},
    
    # Inputs
    "voltage_uin1": {"address": 49, "type": "uint16", "scale": 0.001, "unit": "V", "name": "UIN1 Voltage"},
    "voltage_uin2": {"address": 50, "type": "uint16", "scale": 0.001, "unit": "V", "name": "UIN2 Voltage"},
    "digital_inputs": {"address": 51, "type": "uint16", "name": "Digital Inputs"},
    "battery_voltage": {"address": 52, "type": "uint16", "scale": 0.001, "unit": "V", "name": "RTC Battery Voltage"},
    
    # Zone identification
    "vzv_identify": {"address": 80, "type": "uint16", "name": "Zone Identification"},
}

# Holding Registry - Read/Write
HOLDING_REGISTERS = {
    # Ventilation control
    "ventilation_level": {"address": 0, "type": "uint16", "name": "Ventilation Level", "min": 0, "max": 6},
    
    # Functions with timers (seconds)
    "boost_time": {"address": 1, "type": "uint16", "unit": "s", "name": "Boost Time", "min": 0, "max": 7200},
    "circulation_time": {"address": 2, "type": "uint16", "unit": "s", "name": "Circulation Time", "min": 0, "max": 7200},
    "overpressure_time": {"address": 3, "type": "uint16", "unit": "s", "name": "Overpressure Time", "min": 0, "max": 7200},
    "night_time": {"address": 4, "type": "uint16", "unit": "s", "name": "Night Mode Time", "min": 0, "max": 7200},
    "party_time": {"address": 5, "type": "uint16", "unit": "s", "name": "Party Time", "min": 0, "max": 28800},
    
    # Holiday mode
    "holiday_begin": {"address": 6, "type": "uint32", "name": "Holiday Begin", "timestamp": True},
    "holiday_end": {"address": 8, "type": "uint32", "name": "Holiday End", "timestamp": True},
    
    # Temperature and humidity settings
    "temp_setpoint": {"address": 10, "type": "uint16", "scale": 0.1, "unit": "°C", "name": "Temperature Setpoint", "min": 10, "max": 30},
    "humidity_setpoint": {"address": 11, "type": "uint16", "scale": 0.001, "unit": "%", "name": "Humidity Setpoint", "min": 25, "max": 75},
    
    # Control enables
    "time_program_enable": {"address": 12, "type": "uint16", "name": "Time Program Enable"},
    "antiradon_enable": {"address": 13, "type": "uint16", "name": "Anti-radon Enable"},
    "bypass_enable": {"address": 14, "type": "uint16", "name": "Bypass Enable"},
    "heating_enable": {"address": 15, "type": "uint16", "name": "Heating Enable"},
    "cooling_enable": {"address": 16, "type": "uint16", "name": "Cooling Enable"},
    "comfort_enable": {"address": 17, "type": "uint16", "name": "Comfort Control Enable"},
    
    # VarioBreeze control
    "vb_coolbreeze_priority": {"address": 20, "type": "uint16", "name": "CoolBreeze Priority Control"},
    "vb_kitchen_hood_normal": {"address": 21, "type": "uint16", "name": "Kitchen Hood Normally Open"},
    "vb_boost_volume": {"address": 22, "type": "uint16", "unit": "m³/h", "name": "Zone Boost Volume", "min": 50, "max": 150},
    "vb_kitchen_hood_volume": {"address": 23, "type": "uint16", "unit": "m³/h", "name": "Kitchen Hood Volume", "min": 50, "max": 150},
}

# Zone External Sensors (Zones 1-8)
ZONE_SENSOR_REGISTERS = {}
for zone in range(1, 9):
    base_addr = 300 + (zone - 1) * 10
    ZONE_SENSOR_REGISTERS.update({
        f"zone_{zone}_sensors_present": {"address": base_addr, "type": "uint16", "name": f"Zone {zone} Sensors Present"},
        f"zone_{zone}_sensors_invalidate": {"address": base_addr + 1, "type": "uint16", "name": f"Zone {zone} Sensors Invalidate"},
        f"zone_{zone}_temperature": {"address": base_addr + 2, "type": "int16", "scale": 0.1, "unit": "°C", "name": f"Zone {zone} Temperature", "min": -20, "max": 100},
        f"zone_{zone}_humidity": {"address": base_addr + 3, "type": "uint16", "unit": "%", "name": f"Zone {zone} Humidity", "min": 0, "max": 100},
        f"zone_{zone}_co2": {"address": base_addr + 4, "type": "uint16", "unit": "ppm", "name": f"Zone {zone} CO2", "min": 0, "max": 10000},
        f"zone_{zone}_floor_temperature": {"address": base_addr + 5, "type": "int16", "scale": 0.1, "unit": "°C", "name": f"Zone {zone} Floor Temperature", "min": -20, "max": 100},
    })

# Zone External Buttons (Zones 1-8)  
ZONE_BUTTON_REGISTERS = {}
for zone in range(1, 9):
    base_addr = 400 + (zone - 1) * 10
    ZONE_BUTTON_REGISTERS.update({
        f"zone_{zone}_button_present": {"address": base_addr, "type": "uint16", "name": f"Zone {zone} Button Present"},
        f"zone_{zone}_button_mode": {"address": base_addr + 1, "type": "uint16", "name": f"Zone {zone} Button Mode"},
        f"zone_{zone}_button_timer": {"address": base_addr + 2, "type": "uint16", "unit": "s", "name": f"Zone {zone} Button Timer", "min": 0, "max": 10800},
        f"zone_{zone}_button_active": {"address": base_addr + 3, "type": "uint16", "name": f"Zone {zone} Button Active"},
    })

# Combine all holding registers
HOLDING_REGISTERS.update(ZONE_SENSOR_REGISTERS)
HOLDING_REGISTERS.update(ZONE_BUTTON_REGISTERS)

# Mode definitions based on fut_mode register bits
MODE_BITS = {
    0: "boost_active",
    1: "circulation_active", 
    2: "time_program_active",
    3: "overpressure_active",
    4: "holiday_active",
    5: "party_active",
    6: "night_mode_active",
    7: "antiradon_active",
    8: "device_on",
    9: "filter_check",
    10: "drying",
    11: "bypass_open",
    12: "low_outdoor_temp",
    13: "error_shutdown",
    14: "starting",
    15: "service_mode",
    16: "freeze_protection",
    17: "freeze_protection_active",
    18: "emergency_stop",
    19: "pressure_loss_measurement",
    20: "standby",
    21: "zone_boost",
    22: "zone_pressure_measurement"
}

# Error definitions based on fut_error register bits
ERROR_BITS = {
    0: "ambient_sensor_error",
    1: "indoor_sensor_error", 
    2: "fresh_sensor_error",
    3: "waste_sensor_error",
    4: "supply_fan_error",
    5: "exhaust_fan_error",
    6: "heat_exchanger_comm_error",
    7: "heat_exchanger_valve_error",
    8: "io_board_comm_error",
    9: "supply_fan_blocked",
    10: "exhaust_fan_blocked",
    11: "coolbreeze_comm_error",
    12: "coolbreeze_outdoor_unit_error"
}

# Warning definitions based on fut_warning register bits  
WARNING_BITS = {
    0: "filter_not_initialized",
    1: "filter_dirty",
    2: "filter_overused",
    3: "rtc_battery_low",
    4: "supply_fan_high_rpm",
    5: "exhaust_fan_high_rpm",
    8: "low_outdoor_temp_limited",
    9: "zone_supply_config_error",
    10: "zone_exhaust_config_error", 
    11: "emergency_stop",
    12: "superbreeze_comm_error",
    13: "superbreeze_general_error"
}

# Device configuration bits (fut_config register)
CONFIG_BITS = {
    0: "internal_heating_supported",
    1: "coolbreeze_cooling_available", 
    2: "coolbreeze_heating_available",
    3: "bypass_supported",
    4: "variobreeze_supported",
    5: "internal_circulation_supported",
    6: "coolbreeze_supported",
    7: "heat_exchanger_control_supported"
}

# Zone identification bits (vzv_identify register)
ZONE_BITS = {
    0: "supply_zone_1",
    1: "supply_zone_2",
    2: "supply_zone_3", 
    3: "supply_zone_4",
    4: "supply_zone_5",
    5: "supply_zone_6",
    6: "supply_zone_7",
    7: "supply_zone_8",
    8: "exhaust_zone_1",
    9: "exhaust_zone_2",
    10: "exhaust_zone_3",
    11: "exhaust_zone_4", 
    12: "exhaust_zone_5",
    13: "exhaust_zone_6",
    14: "exhaust_zone_7",
    15: "exhaust_zone_8"
}

# Zone button modes
ZONE_BUTTON_MODES = {
    0: "boost",
    1: "kitchen_hood"
}

# Zone sensor invalidation bits
ZONE_SENSOR_INVALID_BITS = {
    0: "temperature_invalid",
    1: "humidity_invalid", 
    2: "co2_invalid",
    3: "floor_temperature_invalid"
}

# Ventilation levels
VENTILATION_LEVELS = {
    0: "off",
    1: "level_1", 
    2: "level_2",
    3: "level_3", 
    4: "level_4",
    5: "level_5",
    6: "auto"
}

# Device variants
DEVICE_VARIANTS = {
    0: "Futura L",
    1: "Futura L", 
    2: "Futura M"
}

SCAN_INTERVAL = 30  # seconds
