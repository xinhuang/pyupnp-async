import asyncio
import pyupnp
from pprint import pprint

loop = asyncio.get_event_loop()

PORT = '35004'
PROTOCOL = 'UDP'

add_args = {
    'NewRemoteHost': '',
    'NewExternalPort': PORT,           # specify port on router
    'NewProtocol': PROTOCOL,                 # specify protocol
    'NewInternalPort': PORT,           # specify port on internal host
    'NewInternalClient': '192.168.1.7',   # specify IP of internal host
    'NewEnabled': '1',                    # turn mapping ON
    'NewPortMappingDescription': 'Test desc',  # add a description
    'NewLeaseDuration': '0', }              # how long should it be opened?

del_args = {
    'NewRemoteHost': '',
    'NewExternalPort': PORT,
    'NewProtocol': PROTOCOL, }


WANIP_CONNECTION = 'urn:schemas-upnp-org:service:WANIPConnection:1'
WANPPP_CONNECTION = 'urn:schemas-upnp-org:service:WANPPPConnection:1'

DEVICE = 'urn:schemas-upnp-org:device:InternetGatewayDevice:1'

SNAME = WANIP_CONNECTION

async def f():
    service = None
    async for resp in pyupnp.msearch(search_target=DEVICE):
        print('device', resp.src_ip, resp.src_port)
        print(resp.server, resp.st)
        print(resp.location)
        device = await resp.get_device()
        for s in device.filter_service(SNAME):
            service = s
            break
    pprint(service)
    pprint(service.url)
    print('adding port mapping...')
    await service.request('AddPortMapping', add_args)
    print('done')
    await asyncio.sleep(3)
    print('deleting port mapping...')
    await service.request('DeletePortMapping', del_args)
    print('done')


loop.run_until_complete(f())
