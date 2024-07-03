# Sharp Cocoro Air SDK in python

Basically a quick and dirty conversion of https://github.com/dvcrn/cocoro-sdk/ into python. Probably some bugs along the way. 

## Usage:

For auth, read: https://github.com/dvcrn/cocoro-sdk/tree/master?tab=readme-ov-file#authentication

```python
async def main():
    app_secret = ''
    app_key = ''
    # iClub is the default service name, you can also leave it out
    async with Cocoro(app_secret=app_secret, app_key=app_key) as cocoro:
        await cocoro.login()
        devices = await cocoro.query_devices()
        device = devices[0]

        
        all_props = device.get_all_properties()
        for prop in all_props:
            print(prop)
        
        if isinstance(device, Aircon):
            aircon = device

            print("power state")
            print(device.get_power_status())

            device.queue_temperature_update(23.5)
            aircon.queue_power_on()
            device.queue_property_status_update(aircon.get_property_status(StatusCode.OPERATION_MODE))

            print(await cocoro.execute_queued_updates(aircon))
        else:
            print("The first device is not an Aircon")

# Run the async function
asyncio.run(main())
```

## License

MIT