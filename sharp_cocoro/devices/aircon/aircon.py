from typing import Union
from ...device import Device
from ...properties import BinaryPropertyStatus, RangePropertyStatus, SinglePropertyStatus, enum_to_str
from ...state import State8
from .aircon_properties import StatusCode, ValueSingle, FanDirection

class Aircon(Device):
    def get_state8(self) -> State8:
        state8_bin = self.get_property_status(StatusCode.STATE_DETAIL)
        assert isinstance(state8_bin, BinaryPropertyStatus)
        return State8(state8_bin.valueBinary['code'])

    def get_power_status(self) -> ValueSingle:
        status = self.get_property_status(StatusCode.POWER)
        assert isinstance(status, SinglePropertyStatus)
        return ValueSingle(status.valueSingle['code'])

    def get_operation_mode(self) -> ValueSingle:
        status = self.get_property_status(enum_to_str(StatusCode.OPERATION_MODE))
        assert isinstance(status, SinglePropertyStatus)
        return ValueSingle(status.valueSingle['code'])

    def get_temperature(self) -> float:
        return self.get_state8().temperature

    def get_room_temperature(self) -> int:
        room_temp = self.get_property_status(StatusCode.ROOM_TEMPERATURE)
        assert isinstance(room_temp, RangePropertyStatus)
        return int(room_temp.valueRange['code'])

    def get_windspeed(self) -> ValueSingle:
        ws = self.get_property_status(StatusCode.WINDSPEED)
        assert isinstance(ws, SinglePropertyStatus)
        return ValueSingle(ws.valueSingle['code'])

    def get_fan_direction(self) -> FanDirection:
        st = self.get_state8()
        return FanDirection(st.fan_direction)

    def queue_fan_direction_update(self, fs: str) -> None:
        s8 = State8("c20000000000c000000000000000000000000000000000000000000000000000000000000000000000000000000000000101000000000000000000000000000000000000000000000000000000000000")
        s8.fan_direction = int(fs)

        self.queue_property_status_update(BinaryPropertyStatus(StatusCode.STATE_DETAIL, {
            "code": s8.state
        }))

    def queue_temperature_update(self, temp: float) -> None:
        s8 = State8()
        s8.temperature = temp

        self.queue_property_status_update(BinaryPropertyStatus(StatusCode.STATE_DETAIL, {
            "code": s8.state
        }))

        # self.queue_property_status_update({
        #     'statusCode': StatusCode.STATE_DETAIL,
        #     'valueType': ValueType.BINARY,
        #     'valueBinary': {
        #         'code': s8.state
        #     }
        # })

    def queue_power_on(self) -> None:
        self.queue_property_status_update(SinglePropertyStatus(StatusCode.POWER, {
            "code": ValueSingle.POWER_ON.value
        }))

        # self.queue_property_status_update({
        #     'statusCode': StatusCode.POWER,
        #     'valueType': ValueType.SINGLE,
        #     'valueSingle': {
        #         'code': ValueSingle.POWER_ON
        #     }
        # })

    def queue_power_off(self) -> None:
        self.queue_property_status_update(SinglePropertyStatus(StatusCode.POWER, {
            "code": ValueSingle.POWER_OFF.value
        }))

        # self.queue_property_status_update({
        #     'statusCode': StatusCode.POWER,
        #     'valueType': ValueType.SINGLE,
        #     'valueSingle': {
        #         'code': ValueSingle.POWER_OFF
        #     }
        # })

    def queue_operation_mode_update(self, mode: ValueSingle) -> None:
        valid_modes = [
            ValueSingle.OPERATION_OTHER,
            ValueSingle.OPERATION_AUTO,
            ValueSingle.OPERATION_COOL,
            ValueSingle.OPERATION_HEAT,
            ValueSingle.OPERATION_DEHUMIDIFY,
            ValueSingle.OPERATION_VENTILATION
        ]
        if mode not in valid_modes:
            raise ValueError(f"Invalid operation mode: {mode}")

        self.queue_property_status_update(SinglePropertyStatus(StatusCode.OPERATION_MODE, {
            "code": mode.value
        }))

        # self.queue_property_status_update({
        #     'statusCode': StatusCode.OPERATION_MODE,
        #     'valueType': ValueType.SINGLE,
        #     'valueSingle': {
        #         'code': mode
        #     }
        # })

    def queue_windspeed_update(self, mode: Union[ValueSingle, str]) -> None:
        valid_modes = [
            ValueSingle.WINDSPEED_LEVEL_1,
            ValueSingle.WINDSPEED_LEVEL_2,
            ValueSingle.WINDSPEED_LEVEL_3,
            ValueSingle.WINDSPEED_LEVEL_4,
            ValueSingle.WINDSPEED_LEVEL_5,
            ValueSingle.WINDSPEED_LEVEL_6,
            ValueSingle.WINDSPEED_LEVEL_7,
            ValueSingle.WINDSPEED_LEVEL_8,
            ValueSingle.WINDSPEED_LEVEL_AUTO
        ]
        if mode not in valid_modes:
            raise ValueError(f"Invalid windspeed mode: {mode}")

        self.queue_property_status_update(SinglePropertyStatus(StatusCode.WINDSPEED, {
            "code": enum_to_str(mode)
        }))

        # self.queue_property_status_update({
        #     'statusCode': StatusCode.WINDSPEED,
        #     'valueType': ValueType.SINGLE,
        #     'valueSingle': {
        #         'code': mode
        #     }
        # })
