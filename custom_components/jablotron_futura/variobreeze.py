class JablotronFuturaVarioBreezeConfig(CoordinatorEntity):
    """Base class for VarioBreeze configuration entities."""

    def __init__(
        self,
        coordinator: JablotronFuturaCoordinator,
        entity_type: str,
    ) -> None:
        """Initialize the VarioBreeze config entity."""
        super().__init__(coordinator)
        self._entity_type = entity_type
        
        self._attr_unique_id = f"{coordinator.host}_variobreeze_{entity_type}"
        self._attr_name = f"VarioBreeze {entity_type.replace('_', ' ').title()}"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data.get("config_variobreeze_supported", False)
        )


class JablotronFuturaKitchenHoodModeSwitch(JablotronFuturaVarioBreezeConfig, SwitchEntity):
    """Kitchen hood normally open switch for Jablotron Futura."""

    def __init__(self, coordinator: JablotronFuturaCoordinator) -> None:
        """Initialize the kitchen hood mode switch."""
        super().__init__(coordinator, "kitchen_hood_normally_open")
        self._attr_icon = "mdi:stove"

    @property
    def is_on(self) -> bool | None:
        """Return true if kitchen hood is normally open."""
        value = self.coordinator.data.get("vb_kitchen_hood_normal")
        return bool(value) if value is not None else None

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
