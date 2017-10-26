import asyncio
import pyupnp
from pprint import pprint

loop = asyncio.get_event_loop()

arguments = {
    'NewExternalPort': '35000',           # specify port on router
    'NewProtocol': 'TCP',                 # specify protocol
    'NewInternalPort': '35000',           # specify port on internal host
    'NewInternalClient': '192.168.1.7',   # specify IP of internal host
    'NewEnabled': '1',                    # turn mapping ON
    'NewPortMappingDescription': 'Test desc', # add a description
    'NewLeaseDuration': '0',}              # how long should it be opened?

async def f():
    async for resp in pyupnp.msearch(search_target='urn:schemas-upnp-org:device:InternetGatewayDevice:1'):
        print('source', resp.src_ip, resp.src_port)
        print(resp.server, resp.st)
        print(resp.location)
        desc = await resp.get_description()
        for s in desc.filter_service('urn:schemas-upnp-org:service:WANIPConnection:1'):
            pprint(s)
            pprint(s.url)
            await s.request('u:AddPortMapping', 'urn:schemas-upnp-org:service:WANIPConnection:1', arguments)
        for s in desc.filter_service('urn:schemas-upnp-org:service:WANPPPConnection:1'):
            pprint(s)

loop.run_until_complete(f())

