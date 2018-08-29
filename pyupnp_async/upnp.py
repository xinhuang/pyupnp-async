from .device import Device

import asyncio
from datetime import datetime
from async_timeout import timeout
import re
import aiohttp
import xmltodict
import logging

LISTEN_PORT = 65507

logger = logging.getLogger(__name__)


def utcnow():
    return datetime.utcnow().timestamp()


class MSResponse(object):
    def __init__(self, addr, msg):
        self.src_ip = addr[0]
        self.src_port = addr[1]
        logger.debug("MSResponse msg: %s", msg)

        data = dict([(k.upper(), v.lstrip()) for (k,v) in re.findall(r'(?P<name>.*?):(?P<value>.*?)\r\n', msg)])

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
                    self.device = Device(await resp.text(), self.location)

        return self.device


async def msearch(search_target='upnp:rootdevice', max_wait=2, loop=None, first_only=False):
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
            logger.error('error received: %s', exc)

        def connection_lost(self, exc):
            if exc:
                logger.error('connection lost: %s', exc)

        def close(self):
            self.transport.close()

        def timeout(self):
            return self.remaining <= 0

        def cancel(self):
            self.max_wait = 0

        @property
        def remaining(self):
            return self.start_time + self.max_wait - utcnow()

    assert max_wait >= 1 and max_wait <= 120

    loop = loop or asyncio.get_event_loop()

    cp = MSearchClientProtocol(search_target, max_wait, loop)
    await loop.create_datagram_endpoint(
        lambda: cp, local_addr=('0.0.0.0', LISTEN_PORT), reuse_port=True)
    assert cp.start_time

    resp = []
    try:
        async with timeout(cp.remaining, loop=loop):
            while not cp.timeout():
                resp.append(await cp.responses.get())
                if first_only:
                    cp.cancel()
    except asyncio.TimeoutError:
        pass
    except Exception as e:
        logger.error(e)
    finally:
        assert cp.timeout
        cp.close()
        return resp


async def msearch_first(search_target='upnp:rootdevice', max_wait=2, loop=None):
    resp = await msearch(search_target, max_wait, loop, first_only=True)
    if len(resp):
        return resp[0]
