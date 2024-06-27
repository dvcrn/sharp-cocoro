from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Union, Any
from .properties import DeviceType, Property, PropertyStatus, ValueType
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
        # TODO: change to proper type
        self.property_updates: Dict[str, PropertyStatus] = {}
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

    def queue_property_status_update(self, property_status: Dict[str, Any]) -> None:
        status_code = property_status['statusCode']
        for property in self.properties:
            if property.statusCode != status_code:
                continue

            if not property.set:
                raise ValueError(f"property {property.statusName} is not settable")

            # TODO: change to proper type
            self.property_updates[status_code] = property_status
            return

        raise ValueError(f"property {status_code} does not exist on this device")

    def get_property(self, status_code: str) -> Optional[Property]:
        return next((prop for prop in self.properties if prop.statusCode == status_code), None)

    def get_property_status(self, status_code: str) -> Optional[PropertyStatus]:
        return next((status for status in self.status if status.statusCode == status_code), None)