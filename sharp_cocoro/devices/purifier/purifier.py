from ...device import Device
from ...properties import RangePropertyStatus, SinglePropertyStatus
from .purifier_properties import StatusCode, ValueSingle

class Purifier(Device):
    def get_power_status(self) -> ValueSingle:
        status = self.get_property_status(StatusCode.POWER)
        assert isinstance(status, SinglePropertyStatus)
        return ValueSingle(status.valueSingle['code'])

    def get_operation_mode(self) -> ValueSingle:
        status = self.get_property_status(StatusCode.OPERATION_MODE)
        assert isinstance(status, SinglePropertyStatus)
        return ValueSingle(status.valueSingle['code'])

    def get_air_volume(self) -> ValueSingle:
        status = self.get_property_status(StatusCode.AIR_VOLUME)
        assert isinstance(status, SinglePropertyStatus)
        return ValueSingle(status.valueSingle['code'])

    def get_humidity(self) -> int:
        status = self.get_property_status(StatusCode.HUMIDITY)
        assert isinstance(status, RangePropertyStatus)
        return int(status.valueRange['code'])

    def get_room_temperature(self) -> float:
        status = self.get_property_status(StatusCode.ROOM_TEMPERATURE)
        assert isinstance(status, RangePropertyStatus)
        return float(status.valueRange['code']) / 10  # Assuming temperature is in tenths of a degree

    def get_pm25(self) -> int:
        status = self.get_property_status(StatusCode.PM25)
        assert isinstance(status, RangePropertyStatus)
        return int(status.valueRange['code'])

    def get_filter_life(self) -> int:
        status = self.get_property_status(StatusCode.FILTER_LIFE)
        assert isinstance(status, RangePropertyStatus)
        return int(status.valueRange['code'])

    def queue_power_on(self) -> None:
        self.queue_property_status_update(SinglePropertyStatus(StatusCode.POWER, {
            "code": ValueSingle.POWER_ON.value
        }))

    def queue_power_off(self) -> None:
        self.queue_property_status_update(SinglePropertyStatus(StatusCode.POWER, {
            "code": ValueSingle.POWER_OFF.value
        }))

    def queue_operation_mode_update(self, mode: ValueSingle) -> None:
        valid_modes = [
            ValueSingle.OPERATION_AUTO,
            ValueSingle.OPERATION_MANUAL,
            ValueSingle.OPERATION_POLLEN,
            ValueSingle.OPERATION_QUIET
        ]
        if mode not in valid_modes:
            raise ValueError(f"Invalid operation mode: {mode}")

        self.queue_property_status_update(SinglePropertyStatus(StatusCode.OPERATION_MODE, {
            "code": mode.value
        }))

    def queue_air_volume_update(self, volume: ValueSingle) -> None:
        valid_volumes = [
            ValueSingle.AIR_VOLUME_AUTO,
            ValueSingle.AIR_VOLUME_QUIET,
            ValueSingle.AIR_VOLUME_LOW,
            ValueSingle.AIR_VOLUME_MEDIUM,
            ValueSingle.AIR_VOLUME_HIGH,
            ValueSingle.AIR_VOLUME_TURBO
        ]
        if volume not in valid_volumes:
            raise ValueError(f"Invalid air volume: {volume}")

        self.queue_property_status_update(SinglePropertyStatus(StatusCode.AIR_VOLUME, {
            "code": volume.value
        }))
