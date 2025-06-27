from typing import List, Dict, Union, Optional, Any
from .properties import (
    Property,
    PropertyStatus,
    ValueType,
    SingleProperty,
    BinaryProperty,
    RangeProperty,
    SinglePropertyStatus,
    BinaryPropertyStatus,
    RangePropertyStatus,
    ControlResultStatus,
)

from dataclasses import dataclass
import json


@dataclass
class TerminalAppInfo:
    terminalAppId: str
    appName: str
    userNumber: int


@dataclass
class LabelData:
    id: int
    place: str
    name: str
    deviceType: str
    zipCd: str
    yomi: str
    lSubInfo: str

    def __post_init__(self) -> None:
        # Parse lSubInfo if it's a JSON string
        if isinstance(self.lSubInfo, str):
            try:
                self.lSubInfo = json.loads(self.lSubInfo)
            except json.JSONDecodeError:
                pass  # Keep it as a string if it's not valid JSON


@dataclass
class EchonetData:
    maker: str
    series: Optional[str]
    model: str
    serialNumber: Optional[str]
    echonetNode: str
    echonetObject: str
    echonetAttr: str
    echonetProperty: str
    deviceId: int
    simulPerfModeFlag: bool
    propertyUpdatedAt: str
    labelData: LabelData


@dataclass
class DeviceProperty:
    deviceId: int
    echonetNode: str
    echonetObject: str
    registerLevel: int
    label: str
    className: str
    maker: str
    series: str
    model: str
    place: str
    propertyUpdatedAt: str
    property: List[Property]
    status: List[PropertyStatus]


@dataclass
class Box:
    boxId: str
    maxFlag: bool
    pairingFlag: bool
    pairedTerminalNum: int
    timezone: str
    terminalAppInfo: List[TerminalAppInfo]
    echonetData: List[EchonetData]

    def __post_init__(self) -> None:
        # Convert terminalAppInfo dictionaries to TerminalAppInfo objects
        self.terminalAppInfo = [
            TerminalAppInfo(**info) if isinstance(info, dict) else info
            for info in self.terminalAppInfo
        ]

        # Convert echonetData dictionaries to EchonetData objects
        self.echonetData = [
            EchonetData(**data) if isinstance(data, dict) else data
            for data in self.echonetData
        ]

        # For each EchonetData object, convert its labelData dictionary to a LabelData object
        for data in self.echonetData:
            if isinstance(data.labelData, dict):
                data.labelData = LabelData(**data.labelData)


class QueryBoxesResponse:
    def __init__(self, box: List[Dict[str, Any]]):
        self.box = [Box(**item) for item in box]


class QueryDevicePropertiesResponse:
    def __init__(self, device_property: Dict[str, Any]):
        properties: List[Property] = []
        for prop in device_property.get("property", []):
            prop_type = ValueType(prop["valueType"])
            prop_data = {
                k: v
                for k, v in prop.items()
                if k not in ["valueSingle", "valueBinary", "valueRange"]
            }

            if prop_type == ValueType.SINGLE:
                prop_data["valueSingle"] = prop.get("valueSingle", [])
                properties.append(SingleProperty(**prop_data))
            elif prop_type == ValueType.BINARY:
                properties.append(BinaryProperty(**prop_data))
            elif prop_type == ValueType.RANGE:
                prop_data["valueRange"] = prop.get("valueRange", {})
                properties.append(RangeProperty(**prop_data))
            else:
                raise ValueError(f"Unknown property type: {prop_type}")

        statuses: List[PropertyStatus] = []
        for status in device_property.get("status", []):
            status_type = ValueType(status["valueType"])
            status_data = {
                k: v
                for k, v in status.items()
                if k not in ["valueSingle", "valueBinary", "valueRange"]
            }

            if status_type == ValueType.SINGLE:
                status_data["valueSingle"] = status.get("valueSingle", {})
                statuses.append(SinglePropertyStatus(**status_data))
            elif status_type == ValueType.BINARY:
                status_data["valueBinary"] = status.get("valueBinary", {})
                statuses.append(BinaryPropertyStatus(**status_data))
            elif status_type == ValueType.RANGE:
                status_data["valueRange"] = status.get("valueRange", {})
                statuses.append(RangePropertyStatus(**status_data))
            else:
                raise ValueError(f"Unknown status type: {status_type}")

        self.device_property = DeviceProperty(
            **{
                k: v
                for k, v in device_property.items()
                if k not in ["property", "status"]
            },
            property=properties,
            status=statuses,
        )


class ControlListResponse:
    def __init__(self, controlList: List[Dict[str, Union[str, None]]]):
        self.control_list = controlList


@dataclass
class ControlResultItem:
    id: str
    status: ControlResultStatus
    message: Optional[str]
    cancelled_by: Optional[str]
    errorCode: Optional[str]
    epc: str
    edt: str


@dataclass
class ControlResultResponse:
    resultList: List[ControlResultItem]

    def __init__(self, resultList: List[Dict[str, Any]]):
        self.resultList = [
            ControlResultItem(
                id=item["id"],
                status=ControlResultStatus(item["status"]),
                message=item["message"],
                cancelled_by=item["cancelled_by"],
                errorCode=item["errorCode"],
                epc=item["epc"],
                edt=item["edt"],
            )
            for item in resultList
        ]
