# Jablotron Futura Integration

This integration provides comprehensive monitoring and control for Jablotron Futura ventilation units with heat recovery through Home Assistant.

## Features

- **Complete monitoring**: Temperature, humidity, power consumption, fan speeds, filter status
- **Full control**: Ventilation levels, temperature setpoint, function timers, system enables
- **Climate entity**: Unified HVAC control interface
- **Error monitoring**: Real-time error and warning status
- **Czech/English**: Full localization support

## Quick Start

1. Install via HACS
2. Add integration via Settings → Devices & Services
3. Enter your Futura unit's IP address (default: 192.168.1.0)
4. Enjoy comprehensive control and monitoring!

## Requirements

- Jablotron Futura with ModBus TCP interface
- Network connectivity to Home Assistant
- Home Assistant 2023.8+

{% if installed %}
## Configuration

The integration is configured through the UI in Settings → Devices & Services → Add Integration → Jablotron Futura.

Default ModBus TCP settings:
- Port: 502
- Slave ID: 1

{% endif %}

## Documentation

Full documentation available in the [repository README](https://github.com/mtrojan/jablotron-futura-hass).
