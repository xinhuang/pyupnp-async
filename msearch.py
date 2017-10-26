import asyncio
import pyupnp

loop = asyncio.get_event_loop()

async def f():
    async for data in pyupnp.msearch():
        print(data)

loop.run_until_complete(f())

