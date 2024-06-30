from enum import Enum
from typing import Dict, Union, List
from dataclasses import dataclass

def enum_to_str(v):
    # check if v is a enum, if it is we output e.value, if not, just a str
    if isinstance(v, Enum):
        return v.value
    return v

class StatusCode(str, Enum):
    pass

class ValueSingle(str, Enum):
    pass

class DeviceType(str, Enum):
    Unknown = "UNKNOWN"
    AirCondition = "AIR_CON"
    AirCleaner = "AIR_CLEANER"

class RangePropertyType(str, Enum):
    INT = "int"
    FLOAT = "float"

class ValueType(str, Enum):
    SINGLE = "valueSingle"
    BINARY = "valueBinary"
    RANGE = "valueRange"

@dataclass
class Property:
    statusName: str
    statusCode: StatusCode
    get: bool
    set: bool
    inf: bool
    valueType: ValueType

@dataclass
class SingleProperty(Property):
    valueSingle: List[Dict[str, str]]

@dataclass
class BinaryProperty(Property):
    pass

@dataclass
class RangeProperty(Property):
    valueRange: Dict[str, Union[str, RangePropertyType]]

@dataclass
class PropertyStatus:
    statusCode: StatusCode
    valueType: ValueType

    def to_map(self) -> Dict[str, Union[StatusCode, ValueType]]:
        return {
            'statusCode': enum_to_str(self.statusCode),
            "valueType": enum_to_str(self.valueType)
        }

@dataclass
class SinglePropertyStatus(PropertyStatus):
    valueSingle: Dict[str, str]

    def __init__(self, statusCode: Union[str, StatusCode], valueSingle: Dict[str, str], valueType=None):
        super().__init__(statusCode=statusCode, valueType=ValueType.SINGLE)
        self.valueSingle = valueSingle

    def to_map(self) -> Dict[str, Union[str, StatusCode, ValueType, Dict[str, str]]]:
        return {
            **super().to_map(),
            'valueSingle': self.valueSingle
        }

@dataclass
class BinaryPropertyStatus(PropertyStatus):
    valueBinary: Dict[str, str]

    def __init__(self, statusCode: Union[str, StatusCode], valueBinary: Dict[str, str], valueType=None):
        super().__init__(statusCode=statusCode, valueType=ValueType.BINARY)
        self.valueBinary = valueBinary

    def to_map(self) -> Dict[str, Union[str, StatusCode, ValueType, Dict[str, str]]]:
        return {
            **super().to_map(),
            'valueBinary': self.valueBinary
        }

@dataclass
class RangePropertyStatus(PropertyStatus):
    valueRange: Dict[str, Union[str, RangePropertyType]]

    def __init__(self, statusCode: Union[str, StatusCode], valueRange: Dict[str, Union[str, RangePropertyType]], valueType=None):
        super().__init__(statusCode=statusCode, valueType=ValueType.RANGE)
        self.valueRange = valueRange

    def to_map(self) -> Dict[str, Union[str, StatusCode, ValueType, Dict[str, Union[str, RangePropertyType]]]]:
        return {
            **super().to_map(),
            'valueRange': self.valueRange
        }