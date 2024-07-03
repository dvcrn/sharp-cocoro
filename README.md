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

To get a property:
```python
# example: get the operation mode
status = device.get_property_status(StatusCode.OPERATION_MODE.value)
assert isinstance(status, SinglePropertyStatus)
print(ValueSingle(status.valueSingle['code'])) # returns the operation mode
```

To set it: 
```python
device.queue_property_status_update(ValueSingle.OPERATION_COOL)
await cocoro.execute_queued_updates(device)
```

To get an overview of all properties available
```python
device.dump_all_properties()

# 動作状態 (80): ON (30), set=True get=True options=['ON', 'OFF']
# 冷房モード時温度設定値 (B5): None, set=True get=True
# ...
```

Each property also includes information on 

- It's type (binary, single, range)
- Whether it is settable or gettable
- And options that are allowed. In the example above, we can set the power mode only to ON or OFF

## License

MIT