from .factory import service
from .base_service import BaseService
from ..const import LIBRARY_NAME
from ..error import UpnpKeyError

import xmltodict


@service('urn:schemas-upnp-org:service:WANCommonInterfaceConfig:1')
class WANCommonInterfaceConfig(BaseService):
    async def get_total_bytes_sent(self):
        xml = await self.request('GetTotalBytesSent')
        data = xmltodict.parse(xml)
        try:
            return data['s:Envelope']['s:Body']['u:GetTotalBytesSentResponse']['NewTotalBytesSent']
        except KeyError as e:
            raise UpnpKeyError(xml, e.args[0])

    async def get_total_bytes_received(self):
        xml = await self.request('GetTotalBytesReceived')
        data = xmltodict.parse(xml)
        try:
            return data['s:Envelope']['s:Body']['u:GetTotalBytesReceivedResponse']['NewTotalBytesReceived']
        except KeyError as e:
            raise UpnpKeyError(xml, e.args[0])

    async def get_total_packets_sent(self):
        xml = await self.request('GetTotalPacketsSent')
        data = xmltodict.parse(xml)
        try:
            return data['s:Envelope']['s:Body']['u:GetTotalPacketsSentResponse']['NewTotalPacketsSent']
        except KeyError as e:
            raise UpnpKeyError(xml, e.args[0])

    async def get_total_packets_received(self):
        xml = await self.request('GetTotalPacketsReceived')
        data = xmltodict.parse(xml)
        try:
            return data['s:Envelope']['s:Body']['u:GetTotalPacketsReceivedResponse']['NewTotalPacketsReceived']
        except KeyError as e:
            raise UpnpKeyError(xml, e.args[0])

