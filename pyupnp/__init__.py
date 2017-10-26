import asyncio
from datetime import datetime
from async_timeout import timeout


def utcnow():
    return datetime.utcnow().timestamp()


LISTEN_PORT = 65507


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
            self.responses.put_nowait((data, addr))

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
    co = loop.create_datagram_endpoint(
        lambda: cp, local_addr=('0.0.0.0', LISTEN_PORT))
    await co
    print('established')
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
