import asyncio
import pyupnp
from pprint import pprint

loop = asyncio.get_event_loop()

async def f():
    async for resp in pyupnp.msearch(search_target='urn:schemas-upnp-org:device:InternetGatewayDevice:1'):
        print(resp.ip, resp.port)
        print(resp.server, resp.st)
        print(resp.location)
        desc = await resp.get_description()
        for s in desc.filter_service('urn:schemas-upnp-org:service:WANIPConnection:1'):
            pprint(s)
        for s in desc.filter_service('urn:schemas-upnp-org:service:WANPPPConnection:1'):
            pprint(s)

loop.run_until_complete(f())

