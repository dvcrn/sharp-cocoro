# Sharp Cocoro Air SDK in python

Basically a quick and dirty conversion of https://github.com/dvcrn/cocoro-sdk/ into python. Probably some bugs along the way. 

## Usage:

For auth, read: https://github.com/dvcrn/cocoro-sdk/tree/master?tab=readme-ov-file#authentication

```python
import asyncio
from src.cocoro import Cocoro
from src.devices.aircon.aircon import Aircon
from src.devices.aircon.aircon_properties import StatusCode

async def main():
    app_secret = ''
    app_key = ''
    # iClub is the default service name, you can also leave it out
    async with Cocoro(app_secret=app_secret, app_key=app_key) as cocoro:
        await cocoro.login()
        devices = await cocoro.query_devices()
        device = devices[0]

        print("property")
        print(device.get_property(StatusCode.OPERATION_MODE))
        
        # aircon
        if isinstance(device, Aircon):
            aircon = device
            aircon.queue_power_on()
            print(await cocoro.execute_queued_updates(aircon))
        else:
            print("The first device is not an Aircon")

asyncio.run(main())
```

## License

MIT