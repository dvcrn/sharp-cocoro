from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Union, Any
from .properties import DeviceType, Property, PropertyStatus, ValueType, StatusCode, SinglePropertyStatus, RangePropertyStatus, BinaryPropertyStatus, SingleProperty, RangeProperty, BinaryProperty
from .response_types import Box

class Device(ABC):
    def __init__(self, name: str, kind: DeviceType, device_id: int, echonet_node: str, echonet_object: str,
                 properties: List[Property], status: List[PropertyStatus], maker: str, model: str, serial_number: str, box: Box):
        self.name = name
        self.kind = kind
        self.device_id = device_id
        self.echonet_node = echonet_node
        self.echonet_object = echonet_object
        self.properties = properties
        self.status = status
        self.property_updates: Dict[StatusCode, PropertyStatus] = {}
        self.maker = maker
        self.model = model
        self.serial_number = serial_number
        self.box = box

    @abstractmethod
    def queue_power_on(self):
        pass

    @abstractmethod
    def queue_power_off(self):
        pass

    def queue_property_status_update(self, property_status: PropertyStatus) -> None:
        status_code = property_status.statusCode
        for property in self.properties:
            if property.statusCode != status_code:
                continue

            if not property.set:
                raise ValueError(f"property {property.statusName} is not settable")

            self.property_updates[property.statusCode] = property_status
            return

        raise ValueError(f"property {status_code} does not exist on this device")

    def get_all_properties(self) -> List[Property]:
        statuses = self.status
        status_codes = [status.statusCode for status in statuses]

        out = []
        for prop in self.properties:
            if prop.statusCode in status_codes:
                out.append(prop)

        return out
        
    def get_property(self, status_code: str) -> Optional[Property]:
        return next((prop for prop in self.properties if prop.statusCode == status_code), None)

    def get_property_status(self, status_code: str) -> Optional[PropertyStatus]:
        return next((status for status in self.status if status.statusCode == status_code), None)

    def dump_all_properties(self):
        all_props = self.get_all_properties()

        for prop in all_props:
            prop_status = self.get_property_status(prop.statusCode)

            prop_status_value = None
            if isinstance(prop_status, SinglePropertyStatus):
                prop_status_value = prop_status.valueSingle['code']
            elif isinstance(prop_status, BinaryPropertyStatus):
                prop_status_value = prop_status.valueBinary['code']
            elif isinstance(prop_status, RangePropertyStatus):
                prop_status_value = prop_status.valueRange['code']
            else:
                print(prop_status)

            if isinstance(prop, SingleProperty):
                # find the correct entry from valueSingle
                name = prop.code_to_name(prop_status_value)

                print("{} ({}): {} ({}), set={} get={} options={}".format(prop.statusName, prop.statusCode, name, prop_status_value, prop.set, prop.get, prop.names))
            
            else:
                print("{} ({}): {}, set={} get={}".format(prop.statusName, prop.statusCode, prop_status_value, prop.set, prop.get))