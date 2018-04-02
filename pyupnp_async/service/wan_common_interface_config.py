from .factory import service
from .base_service import BaseService
from ..const import LIBRARY_NAME

import xmltodict


@service('urn:schemas-upnp-org:service:WANCommonInterfaceConfig:1')
class WANCommonInterfaceConfig(BaseService):
    async def get_total_bytes_sent(self):
        xml = await self.request('GetTotalBytesSent')
        data = xmltodict.parse(xml)
        return data['s:Envelope']['s:Body']['u:GetTotalBytesSentResponse']['NewTotalBytesSent']

    async def get_total_bytes_received(self):
        xml = await self.request('GetTotalBytesReceived')
        data = xmltodict.parse(xml)
        return data['s:Envelope']['s:Body']['u:GetTotalBytesReceivedResponse']['NewTotalBytesReceived']

    async def get_total_packets_sent(self):
        xml = await self.request('GetTotalPacketsSent')
        data = xmltodict.parse(xml)
        return data['s:Envelope']['s:Body']['u:GetTotalPacketsSentResponse']['NewTotalPacketsSent']

    async def get_total_packets_received(self):
        xml = await self.request('GetTotalPacketsReceived')
        data = xmltodict.parse(xml)
        return data['s:Envelope']['s:Body']['u:GetTotalPacketsReceivedResponse']['NewTotalPacketsReceived']

