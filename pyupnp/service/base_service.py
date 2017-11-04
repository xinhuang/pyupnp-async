from ..error import UpnpSoapError

import xmltodict
import aiohttp
from urllib.parse import urljoin


class BaseService(object):
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
        return xmltodict.unparse(envelop)

    async def request(self, func, params={}):
        urn = self['serviceType']
        data = self.build_request(func, urn, params)
        headers = {'soapaction': '"{urn}#{func}"'.format(urn=urn, func=func),
                   'Content-Type': 'text/xml; charset="utf-8"', }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, data=data, headers=headers) as resp:
                if resp.status == 200:
                    return await resp.text()
                else:
                    raise UpnpSoapError(await resp.text())

    @property
    def url(self):
        return urljoin(self.base_url, self['controlURL'])



