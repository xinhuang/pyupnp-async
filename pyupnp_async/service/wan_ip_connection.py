from .factory import service
from .base_service import BaseService
from ..const import LIBRARY_NAME

import xmltodict


@service('urn:schemas-upnp-org:service:WANIPConnection:1')
@service('urn:schemas-upnp-org:service:WANIPConnection:2')
class WANIPConnectionService(BaseService):
    async def get_external_ip_address(self):
        xml = await self.request('GetExternalIPAddress')
        data = xmltodict.parse(xml)
        return data['s:Envelope']['s:Body']['u:GetExternalIPAddressResponse']['NewExternalIPAddress']

    async def add_port_mapping(self, int_port, ext_port, local_ip, protocol,
                               remote='', enabled=True, lease=0, desc=LIBRARY_NAME):
        args = {
            'NewRemoteHost': remote,
            'NewExternalPort': ext_port,
            'NewProtocol': protocol,
            'NewInternalPort': int_port,
            'NewInternalClient': local_ip,
            'NewEnabled': 1 if enabled else 0,
            'NewPortMappingDescription': desc,
            'NewLeaseDuration': lease, }
        return await self.request('AddPortMapping', args)

    async def delete_port_mapping(self, ext_port, protocol, remote=''):
        args = {
            'NewRemoteHost': remote,
            'NewExternalPort': ext_port,
            'NewProtocol': protocol, }

        return await self.request('DeletePortMapping', args)

