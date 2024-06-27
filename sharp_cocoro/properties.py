from enum import Enum
from typing import Dict, Union, List
from dataclasses import dataclass

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

class RangePropertyType(str, Enum):
    INT = "int"
    FLOAT = "float"

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

@dataclass
class SinglePropertyStatus(PropertyStatus):
    valueSingle: Dict[str, str]

@dataclass
class BinaryPropertyStatus(PropertyStatus):
    valueBinary: Dict[str, str]

@dataclass
class RangePropertyStatus(PropertyStatus):
    valueRange: Dict[str, Union[str, RangePropertyType]]