"""DataUpdateCoordinator for Jablotron Futura."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    SCAN_INTERVAL,
    INPUT_REGISTERS,
    HOLDING_REGISTERS,
    MODE_BITS,
    ERROR_BITS,
    WARNING_BITS,
    CONFIG_BITS,
    ZONE_BITS,
)

_LOGGER = logging.getLogger(__name__)


class JablotronFuturaCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Jablotron Futura."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        slave_id: int,
    ) -> None:
        """Initialize."""
        self.host = host
        self.port = port
        self.slave_id = slave_id
        self._client = ModbusTcpClient(host=host, port=port, timeout=10)
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            return await self._async_read_all_registers()
        except Exception as exception:
            raise UpdateFailed(f"Error communicating with API: {exception}") from exception

    async def _async_read_all_registers(self) -> dict[str, Any]:
        """Read all registers from the device."""
        data = {}
        
        # Connect to device
        connection = await self.hass.async_add_executor_job(self._client.connect)
        if not connection:
            raise UpdateFailed("Unable to connect to device")
            
        try:
            # Read input registers in chunks for efficiency
            input_data = await self._async_read_input_registers()
            holding_data = await self._async_read_holding_registers()
            
            data.update(input_data)
            data.update(holding_data)
            
            # Process special registers
            data.update(self._process_status_registers(data))
            
        finally:
            self._client.close()
            
        return data

    async def _async_read_input_registers(self) -> dict[str, Any]:
        """Read input registers."""
        data = {}
        
        # Read registers in chunks
        chunks = [
            (0, 80),    # Device info, status, temperatures, performance
            (100, 20),  # UI controllers data
            (115, 40),  # Sensors data  
            (160, 80),  # ALFA controllers data
        ]
        
        for start_addr, count in chunks:
            try:
                result = await self.hass.async_add_executor_job(
                    self._client.read_input_registers,
                    start_addr,
                    count,
                    self.slave_id
                )
                
                if result.isError():
                    _LOGGER.warning("Error reading input registers %d-%d: %s", 
                                   start_addr, start_addr + count - 1, result)
                    continue
                    
                # Process registers
                for name, config in INPUT_REGISTERS.items():
                    addr = config["address"]
                    if start_addr <= addr < start_addr + count:
                        data[name] = self._extract_register_value(result.registers, addr - start_addr, config)
                        
            except ModbusException as ex:
                _LOGGER.warning("Modbus error reading input registers %d-%d: %s", 
                               start_addr, start_addr + count - 1, ex)
                
        return data

    async def _async_read_holding_registers(self) -> dict[str, Any]:
        """Read holding registers."""
        data = {}
        
        # Read main holding registers (0-24)
        try:
            result = await self.hass.async_add_executor_job(
                self._client.read_holding_registers,
                0,
                25,
                self.slave_id
            )
            
            if not result.isError():
                for name, config in HOLDING_REGISTERS.items():
                    addr = config["address"]
                    if addr < 25:
                        data[name] = self._extract_register_value(result.registers, addr, config)
                        
        except ModbusException as ex:
            _LOGGER.warning("Modbus error reading holding registers 0-24: %s", ex)

        # Read zone sensor registers (300-374)
        try:
            result = await self.hass.async_add_executor_job(
                self._client.read_holding_registers,
                300,
                75,  # 8 zones * 10 registers per zone - 5 (we only read 5 registers per zone)
                self.slave_id
            )
            
            if not result.isError():
                for name, config in HOLDING_REGISTERS.items():
                    addr = config["address"]
                    if 300 <= addr < 375:
                        offset = addr - 300
                        if offset < len(result.registers):
                            data[name] = self._extract_register_value(result.registers, offset, config)
                        
        except ModbusException as ex:
            _LOGGER.warning("Modbus error reading zone sensor registers: %s", ex)

        # Read zone button registers (400-473)
        try:
            result = await self.hass.async_add_executor_job(
                self._client.read_holding_registers,
                400,
                74,  # 8 zones * 4 registers per zone + some extra
                self.slave_id
            )
            
            if not result.isError():
                for name, config in HOLDING_REGISTERS.items():
                    addr = config["address"]
                    if 400 <= addr < 474:
                        offset = addr - 400
                        if offset < len(result.registers):
                            data[name] = self._extract_register_value(result.registers, offset, config)
                        
        except ModbusException as ex:
            _LOGGER.warning("Modbus error reading zone button registers: %s", ex)
            
        return data

    def _extract_register_value(self, registers: list[int], offset: int, config: dict) -> Any:
        """Extract value from register data based on configuration."""
        reg_type = config["type"]
        
        try:
            if reg_type == "uint16":
                value = registers[offset]
            elif reg_type == "int16":
                value = registers[offset]
                if value > 32767:
                    value -= 65536
            elif reg_type == "uint32":
                value = (registers[offset] << 16) | registers[offset + 1]
            elif reg_type == "int32":
                value = (registers[offset] << 16) | registers[offset + 1]
                if value > 2147483647:
                    value -= 4294967296
            else:
                value = registers[offset]
                
            # Apply scaling if specified
            if "scale" in config:
                value = value * config["scale"]
                
            return value
            
        except (IndexError, ValueError) as ex:
            _LOGGER.warning("Error extracting register value for %s: %s", config.get("name", "unknown"), ex)
            return None

    def _process_status_registers(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process status registers into individual binary sensors."""
        status_data = {}
        
        # Process mode bits
        current_mode = data.get("current_mode", 0)
        if current_mode is not None:
            for bit, name in MODE_BITS.items():
                status_data[f"mode_{name}"] = bool(current_mode & (1 << bit))
                
        # Process error bits
        errors = data.get("errors", 0)
        if errors is not None:
            for bit, name in ERROR_BITS.items():
                status_data[f"error_{name}"] = bool(errors & (1 << bit))
                
        # Process warning bits
        warnings = data.get("warnings", 0)
        if warnings is not None:
            for bit, name in WARNING_BITS.items():
                status_data[f"warning_{name}"] = bool(warnings & (1 << bit))

        # Process config bits (device capabilities)
        device_config = data.get("device_config", 0)
        if device_config is not None:
            for bit, name in CONFIG_BITS.items():
                status_data[f"config_{name}"] = bool(device_config & (1 << bit))

        # Process zone identification bits
        zone_config = data.get("vzv_identify", 0)
        if zone_config is not None:
            for bit, name in ZONE_BITS.items():
                status_data[f"zone_{name}"] = bool(zone_config & (1 << bit))
                
        return status_data

    async def async_write_register(self, address: int, value: int) -> bool:
        """Write a single holding register."""
        try:
            connection = await self.hass.async_add_executor_job(self._client.connect)
            if not connection:
                return False
                
            result = await self.hass.async_add_executor_job(
                self._client.write_register,
                address,
                value,
                self.slave_id
            )
            
            success = not result.isError()
            if success:
                # Trigger immediate data refresh
                await self.async_request_refresh()
            else:
                _LOGGER.error("Error writing register %d: %s", address, result)
                
            return success
            
        except ModbusException as ex:
            _LOGGER.error("Modbus error writing register %d: %s", address, ex)
            return False
        finally:
            self._client.close()

    async def async_write_registers(self, address: int, values: list[int]) -> bool:
        """Write multiple holding registers."""
        try:
            connection = await self.hass.async_add_executor_job(self._client.connect)
            if not connection:
                return False
                
            result = await self.hass.async_add_executor_job(
                self._client.write_registers,
                address,
                values,
                self.slave_id
            )
            
            success = not result.isError()
            if success:
                # Trigger immediate data refresh
                await self.async_request_refresh()
            else:
                _LOGGER.error("Error writing registers %d: %s", address, result)
                
            return success
            
        except ModbusException as ex:
            _LOGGER.error("Modbus error writing registers %d: %s", address, ex)
            return False
        finally:
            self._client.close()
