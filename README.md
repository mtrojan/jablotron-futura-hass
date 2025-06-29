# Jablotron Futura Integration for Home Assistant

Custom integration for Jablotron Futura ventilation units with heat recovery, providing comprehensive monitoring and control through Home Assistant.

## Features

### Core Sensors
- **Temperature sensors**: Outdoor, supply, extract, and exhaust air temperatures, external NTC sensor
- **Humidity sensors**: Air humidity for all air streams
- **Performance monitoring**: Power consumption, heat recovery efficiency, heating power
- **Fan monitoring**: PWM levels and RPM for both supply and exhaust fans
- **System monitoring**: Filter wear level, air flow rate, input voltages
- **Device information**: Serial number, firmware version, hardware version, device variant

### VarioBreeze Zone Control (if supported)
- **Zone sensors**: Temperature, humidity, CO2, floor temperature for up to 8 zones
- **Zone controls**: Button mode selection (Boost/Kitchen Hood), timer settings
- **Zone status**: Real-time monitoring of zone sensor presence and button activity
- **Kitchen hood integration**: Configurable normally open/closed damper control

### CoolBreeze Climate Control (if supported)  
- **Heat pump operation**: Heating and cooling control
- **Climate entity**: Dedicated CoolBreeze climate control with auto mode
- **Priority control**: CO2 vs temperature priority for automatic operation
- **Performance monitoring**: Real-time heating/cooling output tracking

### Core Controls
- **Ventilation level control**: 6 levels (Off, 1-5, Auto)
- **Temperature setpoint**: Adjustable target temperature (10-30°C)
- **Function timers**: Boost, circulation, overpressure, night mode, party mode
- **System enables**: Time program, anti-radon protection, bypass, heating, cooling, comfort control
- **Climate entity**: Unified HVAC control with temperature and fan mode settings

### Status Monitoring
- **Operating modes**: Real-time status of all device functions
- **Error monitoring**: Comprehensive error and warning reporting with individual binary sensors
- **System status**: Device state, filter condition, bypass status
- **Capability detection**: Automatic detection of available features (VarioBreeze, CoolBreeze, bypass, etc.)

## Requirements

- Home Assistant 2023.8 or newer
- Jablotron Futura ventilation unit with ModBus TCP interface
- Network connectivity between Home Assistant and the Futura unit

## Installation

### HACS Installation (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/your_username/jablotron_futura`
6. Select "Integration" as the category
7. Click "Add"
8. Search for "Jablotron Futura" and install

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/your_username/jablotron_futura/releases)
2. Extract the `jablotron_futura` folder to your `custom_components` directory
3. Restart Home Assistant

## Configuration

### Basic Setup

1. Go to Settings → Devices & Services
2. Click "Add Integration"
3. Search for "Jablotron Futura"
4. Enter your device configuration:
   - **IP Address**: The IP address of your Futura unit (default: 192.168.1.0)
   - **Port**: ModBus TCP port (default: 502)
   - **Slave ID**: ModBus slave ID (default: 1)
   - **Name**: Friendly name for the integration

### Network Configuration

Ensure your Jablotron Futura unit is connected to your network and accessible from Home Assistant. The default network settings are:
- IP Address: 192.168.1.0
- Port: 502
- Slave ID: 1

You may need to configure your network to route traffic to the Futura unit or place it on the same subnet as Home Assistant.

## Device Information

The integration automatically detects the device variant:
- **Futura L**: Compact model
- **Futura M**: Medium model

Device information includes:
- Serial number (used for unique device identification)
- Hardware revision
- Firmware version
- Register map version
- Available features (heating, cooling, bypass, etc.)

## Available Entities

### Core Sensors

| Entity | Description | Unit |
|--------|-------------|------|
| `sensor.futura_outdoor_air_temperature` | Outside air temperature | °C |
| `sensor.futura_supply_air_temperature` | Supply air temperature | °C |
| `sensor.futura_extract_air_temperature` | Extract air temperature | °C |
| `sensor.futura_exhaust_air_temperature` | Exhaust air temperature | °C |
| `sensor.futura_outdoor_air_humidity` | Outside air humidity | % |
| `sensor.futura_supply_air_humidity` | Supply air humidity | % |
| `sensor.futura_extract_air_humidity` | Extract air humidity | % |
| `sensor.futura_exhaust_air_humidity` | Exhaust air humidity | % |
| `sensor.futura_power_consumption` | Current power consumption | W |
| `sensor.futura_heat_recovery` | Heat recovery power | W |
| `sensor.futura_heating_power` | Heating power | W |
| `sensor.futura_air_flow` | Air flow rate | m³/h |
| `sensor.futura_filter_wear_level` | Filter contamination level | % |
| `sensor.futura_supply_fan_pwm` | Supply fan PWM level | % |
| `sensor.futura_exhaust_fan_pwm` | Exhaust fan PWM level | % |
| `sensor.futura_supply_fan_rpm` | Supply fan speed | rpm |
| `sensor.futura_exhaust_fan_rpm` | Exhaust fan speed | rpm |

### VarioBreeze Zone Sensors (if supported)

| Entity Pattern | Description | Unit |
|----------------|-------------|------|
| `sensor.futura_zone_X_temperature` | Zone X temperature | °C |
| `sensor.futura_zone_X_humidity` | Zone X humidity | % |
| `sensor.futura_zone_X_co2` | Zone X CO2 concentration | ppm |
| `sensor.futura_zone_X_floor_temperature` | Zone X floor temperature | °C |

### Core Controls

| Entity | Description | Values |
|--------|-------------|--------|
| `select.futura_ventilation_level` | Ventilation level | Off, Level 1-5, Auto |
| `switch.futura_time_program` | Time program enable | On/Off |
| `switch.futura_anti_radon_protection` | Anti-radon protection | On/Off |
| `switch.futura_bypass` | Bypass enable | On/Off |
| `switch.futura_heating` | Heating enable | On/Off |
| `switch.futura_cooling` | Cooling enable | On/Off |
| `switch.futura_comfort_control` | Comfort control enable | On/Off |
| `number.futura_boost_time` | Boost function timer | 0-7200 s |
| `number.futura_circulation_time` | Circulation timer | 0-7200 s |
| `number.futura_overpressure_time` | Overpressure timer | 0-7200 s |
| `number.futura_night_time` | Night mode timer | 0-7200 s |
| `number.futura_party_time` | Party mode timer | 0-28800 s |
| `climate.futura_climate` | Main climate control | HVAC modes, temperature, fan |

### VarioBreeze Zone Controls (if supported)

| Entity Pattern | Description | Values |
|----------------|-------------|--------|
| `select.futura_zone_X_button_mode` | Zone X button mode | Boost, Kitchen Hood |
| `number.futura_zone_X_button_timer` | Zone X button timer | 0-10800 s |
| `switch.futura_zone_X_button_active` | Zone X button active | On/Off |

### CoolBreeze Controls (if supported)

| Entity | Description | Values |
|--------|-------------|--------|
| `climate.futura_coolbreeze_climate` | CoolBreeze climate control | Heat/Cool/Auto modes |
| `sensor.futura_coolbreeze_output` | CoolBreeze output level | % |
| `switch.futura_coolbreeze_auto_priority` | CO2 vs Temperature priority | On/Off |
| `switch.futura_kitchen_hood_normally_open` | Kitchen hood damper mode | On/Off |

### Status Monitoring (Binary Sensors)

| Entity Pattern | Description |
|----------------|-------------|
| `binary_sensor.futura_mode_*` | Operating mode status (boost, circulation, etc.) |
| `binary_sensor.futura_error_*` | Error conditions (sensor errors, fan errors, etc.) |
| `binary_sensor.futura_warning_*` | Warning conditions (filter status, battery, etc.) |
| `binary_sensor.futura_config_*` | Device capabilities (CoolBreeze, VarioBreeze, etc.) |
| `binary_sensor.futura_zone_*` | Zone configuration status |

## Usage Examples

### Automation Examples

#### Automatic Zone Boost when CO2 is High
```yaml
automation:
  - alias: "Futura: Zone 1 Boost on High CO2"
    trigger:
      - platform: numeric_state
        entity_id: sensor.futura_zone_1_co2
        above: 1000
    condition:
      - condition: state
        entity_id: binary_sensor.futura_zone_1_sensors_present
        state: "on"
    action:
      - service: number.set_value
        target:
          entity_id: number.futura_zone_1_button_timer
        data:
          value: 1800  # 30 minutes
      - service: switch.turn_on
        target:
          entity_id: switch.futura_zone_1_button_active

#### Kitchen Hood Auto-Activation
```yaml
automation:
  - alias: "Futura: Kitchen Hood Auto Start"
    trigger:
      - platform: numeric_state
        entity_id: sensor.futura_zone_2_humidity  # Assuming zone 2 is kitchen
        above: 70
    condition:
      - condition: state
        entity_id: select.futura_zone_2_button_mode
        state: "kitchen_hood"
    action:
      - service: number.set_value
        target:
          entity_id: number.futura_zone_2_button_timer
        data:
          value: 900  # 15 minutes
      - service: switch.turn_on
        target:
          entity_id: switch.futura_zone_2_button_active

#### CoolBreeze Smart Control
```yaml
automation:
  - alias: "Futura: CoolBreeze Auto Summer Mode"
    trigger:
      - platform: numeric_state
        entity_id: sensor.futura_outdoor_air_temperature
        above: 25
      - platform: time
        at: "08:00:00"
    condition:
      - condition: state
        entity_id: binary_sensor.futura_config_coolbreeze_supported
        state: "on"
      - condition: numeric_state
        entity_id: sensor.futura_outdoor_air_temperature
        above: 20
    action:
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.futura_coolbreeze_climate
        data:
          hvac_mode: "cool"
      - service: climate.set_temperature
        target:
          entity_id: climate.futura_coolbreeze_climate
        data:
          temperature: 23

#### Automatic Boost when Humidity is High (Original)
```yaml
automation:
  - alias: "Futura: Boost on High Humidity"
    trigger:
      - platform: numeric_state
        entity_id: sensor.futura_extract_air_humidity
        above: 70
    action:
      - service: number.set_value
        target:
          entity_id: number.futura_boost_time
        data:
          value: 1800  # 30 minutes
```

#### Filter Change Reminder
```yaml
automation:
  - alias: "Futura: Filter Change Reminder"
    trigger:
      - platform: numeric_state
        entity_id: sensor.futura_filter_wear_level
        above: 80
    action:
      - service: persistent_notification.create
        data:
          title: "Futura Filter Maintenance"
          message: "Filter wear level is {{ states('sensor.futura_filter_wear_level') }}%. Consider changing filters."

#### Error Alert System
```yaml
automation:
  - alias: "Futura: Error Alert"
    trigger:
      - platform: state
        entity_id: 
          - binary_sensor.futura_error_supply_fan_error
          - binary_sensor.futura_error_exhaust_fan_error
          - binary_sensor.futura_error_ambient_sensor_error
        to: "on"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "Futura Error"
          message: "Error detected: {{ trigger.to_state.name }}"
          data:
            priority: high

#### Night Mode Schedule
```yaml
automation:
  - alias: "Futura: Night Mode"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: number.set_value
        target:
          entity_id: number.futura_night_time
        data:
          value: 28800  # 8 hours
```

### Dashboard Card Examples

#### Main Futura Overview Card
```yaml
type: entities
title: Jablotron Futura
entities:
  - entity: climate.futura_climate
  - entity: select.futura_ventilation_level
  - entity: sensor.futura_outdoor_air_temperature
  - entity: sensor.futura_supply_air_temperature
  - entity: sensor.futura_extract_air_temperature
  - entity: sensor.futura_air_flow
  - entity: sensor.futura_filter_wear_level
  - entity: sensor.futura_power_consumption
```

#### VarioBreeze Zone Control Card
```yaml
type: vertical-stack
title: VarioBreeze Zones
cards:
  - type: horizontal-stack
    cards:
      - type: entities
        title: Living Room (Zone 1)
        entities:
          - sensor.futura_zone_1_temperature
          - sensor.futura_zone_1_humidity
          - sensor.futura_zone_1_co2
          - select.futura_zone_1_button_mode
          - switch.futura_zone_1_button_active
      - type: entities
        title: Kitchen (Zone 2)
        entities:
          - sensor.futura_zone_2_temperature
          - sensor.futura_zone_2_humidity
          - sensor.futura_zone_2_co2
          - select.futura_zone_2_button_mode
          - switch.futura_zone_2_button_active
```

#### CoolBreeze Control Card
```yaml
type: entities
title: CoolBreeze Climate
show_header_toggle: false
entities:
  - entity: climate.futura_coolbreeze_climate
  - entity: sensor.futura_coolbreeze_output
  - entity: switch.futura_coolbreeze_auto_priority
  - entity: switch.futura_kitchen_hood_normally_open
```

#### System Status Card
```yaml
type: entities
title: Futura System Status
entities:
  - entity: binary_sensor.futura_mode_device_on
    icon: mdi:power
  - entity: binary_sensor.futura_mode_boost_active
    icon: mdi:fan-plus
  - entity: binary_sensor.futura_mode_bypass_open
    icon: mdi:valve-open
  - entity: binary_sensor.futura_warning_filter_dirty
    icon: mdi:air-filter
  - entity: binary_sensor.futura_error_supply_fan_error
    icon: mdi:fan-alert
  - entity: binary_sensor.futura_error_exhaust_fan_error
    icon: mdi:fan-alert
```

#### Air Quality Overview Card
```yaml
type: glance
title: Air Quality
entities:
  - entity: sensor.futura_zone_1_co2
    name: Living Room CO2
  - entity: sensor.futura_zone_2_co2
    name: Kitchen CO2
  - entity: sensor.futura_zone_3_co2
    name: Bedroom CO2
  - entity: sensor.futura_extract_air_humidity
    name: Humidity
columns: 2
```

## Troubleshooting

### Connection Issues
- Verify the IP address and network connectivity
- Check that ModBus TCP is enabled on the Futura unit
- Ensure no firewall is blocking port 502
- Verify the slave ID matches the device configuration

### Data Not Updating
- Check the Home Assistant logs for error messages
- Verify the device is powered on and responsive
- Try restarting the integration from the Integrations page

### Missing Entities
- Some entities may not be available depending on your device variant
- Check the device configuration register to see available features
- Restart Home Assistant after installation

## Support

For issues and feature requests, please use the [GitHub issues page](https://github.com/your_username/jablotron_futura/issues).

## Contributing

Contributions are welcome! Please read the contributing guidelines and submit pull requests for any improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This integration is not officially supported by Jablotron Living Technology. Use at your own risk.
