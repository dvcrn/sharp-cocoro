from ..device import Device
import sys

class UnknownDevice(Device):
    def queue_power_off(self) -> None:
        print("Error: not implemented", file=sys.stderr)

    def queue_power_on(self) -> None:
        print("Error: not implemented", file=sys.stderr)