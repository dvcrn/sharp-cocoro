from typing import Optional
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
    """
    Example

    SingleProperty(statusName='風量設定', statusCode='A0', get=True, set=True, inf=False, valueType='valueSingle', valueSingle=[{'name': '風量レベル1', 'code': '31'}, {'name': '風量レベル2', 'code': '32'}, {'name': '風量レベル3', 'code': '33'}, {'name': '風量レベル4', 'code': '34'}, {'name': '風量レベル5', 'code': '35'}, {'name': '風量レベル6', 'code': '36'}, {'name': '風量レベル7', 'code': '37'}, {'name': '風量レベル8', 'code': '38'}, {'name': '風量自動設定', 'code': '41'}])
    """
    valueSingle: List[Dict[str, str]]

    def supported_codes(self) -> List[str]:
        return [v['code'] for v in self.valueSingle]

    def supports_code(self, code: str) -> bool:
        return code in self.supported_codes

    @property
    def names(self) -> List[str]:
        return [v['name'] for v in self.valueSingle]

    @property
    def code_map(self) -> Dict[str, str]:
        return {v['code']: v['name'] for v in self.valueSingle}
        
    def code_to_name(self, code: str) -> Optional[str]:
        return self.code_map.get(code, None)    

    def name_to_code(self, name: str) -> Optional[str]:
        code_map = {v['name']: v['code'] for v in self.valueSingle}
        return code_map.get(name, None)


@dataclass
class BinaryProperty(Property):
    pass

@dataclass
class RangeProperty(Property):
    """
    Example: 
    RangeProperty(statusName='除湿モード時温度設定値', statusCode='B7', get=True, set=True, inf=False, valueType='valueRange', valueRange={'type': 'int', 'min': '0', 'max': '60', 'step': '1', 'unit': '℃'})
    RangeProperty(statusName='相対温度設定値', statusCode='BF', get=True, set=True, inf=False, valueType='valueRange', valueRange={'type': 'float', 'min': '-127', 'max': '125', 'step': '0.1', 'unit': '℃'})
    """
    valueRange: Dict[str, Union[str, RangePropertyType]]

    @property
    def range_type(self) -> str:
        return self.valueRange['type']

    @property
    def range_min(self) -> str:
        return self.valueRange['min']

    @property
    def range_max(self) -> str:
        return self.valueRange['max']

    @property
    def range_step(self) -> str:
        return self.valueRange['max']

    @property
    def unit(self) -> str:
        return self.valueRange['unit']

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