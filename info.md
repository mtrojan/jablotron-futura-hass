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

# =============================================================================
# LICENSE - MIT License
# =============================================================================
MIT License

Copyright (c) 2025 Martin Trojan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
