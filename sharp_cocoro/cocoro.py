import httpx
import asyncio
import time
from typing import List, Dict, Any, Union, Optional, Sequence, cast
from .properties import DeviceType, PropertyStatus, Property, ControlResultStatus
from .response_types import (
    Box,
    QueryBoxesResponse,
    QueryDevicePropertiesResponse,
    ControlListResponse,
    ControlResultResponse,
)
from .device import Device
from .devices.aircon.aircon import Aircon
from .devices.purifier.purifier import Purifier
from .devices.unknown import UnknownDevice
from .http_adapter import HTTPAdapter, create_adapter


class Cocoro:
    def __init__(
        self, app_secret: str, app_key: str, service_name: str = "iClub", session=None
    ):
        self.app_secret = app_secret
        self.app_key = app_key
        self.service_name = service_name
        self.is_authenticated = False
        self.api_base = "https://hms.cloudlabs.sharp.co.jp/hems/pfApi/ta"
        self.headers = {
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "smartlink_v200i Mozilla/5.0 (iPad; CPU OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
        }
        # Create HTTP adapter
        self._adapter: HTTPAdapter = create_adapter(
            session=session, headers=self.headers
        )
        # Keep session reference for backward compatibility
        self.session = session if isinstance(session, httpx.AsyncClient) else None

    async def __aenter__(self) -> "Cocoro":
        # No need to create session, adapter handles it
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[Any],
    ) -> None:
        await self.close()

    async def close(self) -> None:
        await self._adapter.close()
        self.session = None

    async def _create_session(self) -> None:
        # Deprecated - adapter handles session management
        pass

    async def send_get_request(self, path: str) -> Dict[str, Any]:
        return await self._adapter.get(f"{self.api_base}{path}")

    async def send_post_request(
        self, path: str, body: Dict[str, Any]
    ) -> Dict[str, Any]:
        return await self._adapter.post(f"{self.api_base}{path}", body)

    @staticmethod
    def device_type_from_string(s: str) -> DeviceType:
        return DeviceType(s)

    async def login(self) -> Dict[str, str]:
        json_res = await self.send_post_request(
            f"/setting/login/?appSecret={self.app_secret}&serviceName={self.service_name}",
            {
                "terminalAppId": f"https://db.cloudlabs.sharp.co.jp/clpf/key/{self.app_key}"
            },
        )
        self.is_authenticated = True
        return json_res

    async def query_boxes(self) -> List[Box]:
        res = await self.send_get_request(
            f"/setting/boxInfo/?appSecret={self.app_secret}&mode=other"
        )
        res_parsed = QueryBoxesResponse(**res)
        return res_parsed.box

    async def query_box_properties(
        self, box: Box
    ) -> Dict[str, Union[List[Property], List[PropertyStatus]]]:
        echonet_data = box.echonetData[0]
        res = await self.send_get_request(
            f"/control/deviceProperty?boxId={box.boxId}&appSecret={self.app_secret}"
            f"&echonetNode={echonet_data.echonetNode}&echonetObject={echonet_data.echonetObject}&status=true"
        )
        res_parsed = QueryDevicePropertiesResponse(
            device_property=res["deviceProperty"]
        )
        return {
            "properties": res_parsed.device_property.property,
            "status": res_parsed.device_property.status,
        }

    async def query_devices(self) -> Sequence[Device]:
        boxes = await self.query_boxes()
        devices: List[Device] = []

        for box in boxes:
            properties_and_status = await self.query_box_properties(box)
            properties = cast(List[Property], properties_and_status["properties"])
            status = cast(List[PropertyStatus], properties_and_status["status"])

            device_type = self.device_type_from_string(
                box.echonetData[0].labelData.deviceType
            )

            echonet_data = box.echonetData[0]
            name = echonet_data.labelData.name
            device_id = echonet_data.deviceId
            echonet_node = echonet_data.echonetNode
            echonet_object = echonet_data.echonetObject
            maker = echonet_data.maker
            model = echonet_data.model
            serial_number = echonet_data.serialNumber or ""

            if device_type == DeviceType.AirCleaner:
                devices.append(
                    Purifier(
                        name=name,
                        kind=device_type,
                        device_id=device_id,
                        echonet_node=echonet_node,
                        echonet_object=echonet_object,
                        properties=properties,
                        status=status,
                        maker=maker,
                        model=model,
                        serial_number=serial_number,
                        box=box,
                    )
                )
            elif device_type == DeviceType.AirCondition:
                devices.append(
                    Aircon(
                        name=name,
                        kind=device_type,
                        device_id=device_id,
                        echonet_node=echonet_node,
                        echonet_object=echonet_object,
                        properties=properties,
                        status=status,
                        maker=maker,
                        model=model,
                        serial_number=serial_number,
                        box=box,
                    )
                )
            else:
                devices.append(
                    UnknownDevice(
                        name=name,
                        kind=device_type,
                        device_id=device_id,
                        echonet_node=echonet_node,
                        echonet_object=echonet_object,
                        properties=properties,
                        status=status,
                        maker=maker,
                        model=model,
                        serial_number=serial_number,
                        box=box,
                    )
                )

        return devices

    async def execute_queued_updates(self, device: Device) -> Dict[str, Any]:
        status_map: List[Dict[str, Any]] = []
        for _, val in device.property_updates.items():
            status_map.append(val.to_map())

        body = {
            "controlList": [
                {
                    "deviceId": device.device_id,
                    "echonetNode": device.echonet_node,
                    "echonetObject": device.echonet_object,
                    "status": status_map,
                }
            ]
        }

        json_body = await self.send_post_request(
            f"/control/deviceControl?boxId={device.box.boxId}&appSecret={self.app_secret}",
            body,
        )

        control_list_response = ControlListResponse(**json_body)

        if control_list_response.control_list:
            errors = [
                f"{row['id']}={row['errorCode']}"
                for row in control_list_response.control_list
                if row["errorCode"] and row["errorCode"] != ""
            ]

            if errors:
                raise Exception("Cocoro API Error: " + ",".join(errors))

        for status in device.property_updates.values():
            for i, s in enumerate(device.status):
                if s.statusCode == status.statusCode:
                    device.status[i] = status

        device.property_updates.clear()

        return json_body

    async def check_control_results(
        self, device: Device, control_ids: List[str]
    ) -> ControlResultResponse:
        """
        Check the status of control commands by their IDs.

        Args:
            device: The device that was controlled
            control_ids: List of control IDs to check

        Returns:
            ControlResultResponse with current status of each control
        """
        body = {"resultList": [{"id": control_id} for control_id in control_ids]}

        json_body = await self.send_post_request(
            f"/control/controlResult?boxId={device.box.boxId}&appSecret={self.app_secret}",
            body,
        )

        return ControlResultResponse(**json_body)

    async def wait_for_control_completion(
        self,
        device: Device,
        control_ids: List[str],
        timeout: float = 30.0,
        poll_interval: float = 1.0,
    ) -> ControlResultResponse:
        """
        Poll control results until all commands are completed or timeout.

        Args:
            device: Device that was controlled
            control_ids: List of control IDs to monitor
            timeout: Maximum time to wait in seconds
            poll_interval: Time between polls in seconds

        Returns:
            Final ControlResultResponse when all controls are done

        Raises:
            TimeoutError: If timeout is exceeded
            Exception: If any control has an error
        """
        start_time = time.time()

        while True:
            # Check if we've exceeded the timeout
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Control completion timed out after {timeout} seconds"
                )

            # Poll the current status
            result = await self.check_control_results(device, control_ids)

            # Check if all controls are finished (success or unmatch)
            finished_states = {ControlResultStatus.SUCCESS, ControlResultStatus.UNMATCH}
            all_finished = all(
                item.status in finished_states for item in result.resultList
            )

            if all_finished:
                return result

            # Check for any error states
            error_items = [
                item
                for item in result.resultList
                if item.errorCode and item.errorCode != ""
            ]
            if error_items:
                error_messages = [
                    f"Control {item.id}: {item.errorCode}" for item in error_items
                ]
                raise Exception("Control errors: " + ", ".join(error_messages))

            # Wait before next poll
            await asyncio.sleep(poll_interval)

    async def fetch_device(self, device: Device) -> Device:
        devices = await self.query_devices()
        for d in devices:
            if d.device_id == device.device_id:
                return d

        raise Exception("device does not exist")
