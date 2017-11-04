import asyncio
from datetime import datetime
from async_timeout import timeout
import re
import aiohttp
import xmltodict
from urllib.parse import urljoin

LISTEN_PORT = 65507


class UpnpSoapError(Exception):
    def __init__(self, xmlstr):
        self.data = xmltodict.parse(xmlstr)

        detail = self.data['s:Envelope']['s:Body']['s:Fault']['detail']
        self.error_code = int(detail['UPnPError']['errorCode'])

    def __str__(self):
        return self.data


def utcnow():
    return datetime.utcnow().timestamp()


class Service(object):
    def __init__(self, base_url, data):
        self.base_url = base_url
        self.data = data

    def __getitem__(self, key):
        return self.data[key]

    def __str__(self):
        return self.data.__str__()

    def __repr__(self):
        return self.data.__repr__()

    def build_request(self, func, urn, params):
        params['@xmlns:u'] = urn
        envelop = {'s:Envelope': {
            '@xmlns:s': 'http://schemas.xmlsoap.org/soap/envelope/',
            '@s:encodingStyle': 'http://schemas.xmlsoap.org/soap/encoding/',
            's:Body': {'u:' + func: params}}}
        return xmltodict.unparse(envelop).replace(' encoding="utf-8"', '')

    async def request(self, func, params):
        urn = self['serviceType']
        data = self.build_request(func, urn, params)
        headers = {'soapaction': '"{urn}#{func}"'.format(urn=urn, func=func),
                   'Content-Type': 'text/xml; charset="utf-8"', }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, data=data, headers=headers) as resp:
                if resp.status == 200:
                    pass
                else:
                    raise UpnpSoapError(await resp.text())

    @property
    def url(self):
        return urljoin(self.base_url, self['controlURL'])


class Device(object):
    def __init__(self, data):
        self.data = xmltodict.parse(data)

    def __getitem__(self, key):
        return self.data[key]

    def __str__(self):
        return self.data.__str__()

    def __repr__(self):
        return self.data.__repr__()

    @property
    def url_base(self):
        return self['root']['URLBase']

    def filter_service(self, stype):
        def _filter(device, stype):
            slist = device.get('serviceList')
            if slist:
                slist = slist.get('service')
                slist = slist if isinstance(slist, list) else [slist]
                for s in slist:
                    if s.get('serviceType') == stype:
                        yield Service(self.url_base, s)
            dlist = device.get('deviceList')
            if dlist:
                dlist = dlist.get('device')
                dlist = dlist if isinstance(dlist, list) else [dlist]
                for d in dlist:
                    for s in _filter(d, stype):
                        yield s
        return _filter(self.data['root']['device'], stype)


class MSResponse(object):
    def __init__(self, addr, msg):
        self.src_ip = addr[0]
        self.src_port = addr[1]
        data = dict(re.findall(r'(?P<name>.*?): (?P<value>.*?)\r\n', msg))
        self.st = data['ST']
        self.usn = data['USN']
        self.server = data['SERVER']
        self.location = data['LOCATION']
        self.date = data.get('DATE')
        self.cache_control = data.get('CACHE-CONTROL')
        self.device = None

    async def get_device(self):
        assert self.location

        if self.device is None:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.location) as resp:
                    self.device = Device(await resp.text())

        return self.device


async def msearch(search_target='upnp:rootdevice', max_wait=2, loop=None):
    class MSearchClientProtocol(object):
        def __init__(self, search_target, max_wait, loop):
            self.transport = None
            self.msg = \
                'M-SEARCH * HTTP/1.1\r\n' \
                'HOST:239.255.255.250:1900\r\n' \
                'ST:{st}\r\n' \
                'MX:{mx}\r\n' \
                'MAN:"ssdp:discover"\r\n' \
                '\r\n'.format(st=search_target, mx=max_wait)

            self.responses = asyncio.Queue(loop=loop)
            self.start_time = None
            self.max_wait = max_wait
            self.ip = '239.255.255.250'
            self.port = 1900

        def connection_made(self, transport):
            self.transport = transport
            self.transport.sendto(self.msg.encode(), addr=(self.ip, self.port))
            self.start_time = utcnow()

        def datagram_received(self, data, addr):
            self.responses.put_nowait(MSResponse(addr, data.decode()))

        def error_received(self, exc):
            print('error received:', exc)

        def connection_lost(self, exc):
            if exc:
                print('connection lost:', exc)

        def close(self):
            self.transport.close()

        def timeout(self):
            return self.remaining <= 0

        @property
        def remaining(self):
            return self.start_time + self.max_wait - utcnow()

    assert max_wait >= 1 and max_wait <= 120

    loop = loop or asyncio.get_event_loop()

    cp = MSearchClientProtocol(search_target, max_wait, loop)
    await loop.create_datagram_endpoint(
        lambda: cp, local_addr=('0.0.0.0', LISTEN_PORT))
    assert cp.start_time

    try:
        async with timeout(cp.remaining, loop=loop):
            while not cp.timeout():
                yield await cp.responses.get()
    except asyncio.TimeoutError:
        pass
    except Exception as e:
        print(e)
    finally:
        assert cp.timeout
        cp.close()
