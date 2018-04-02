from .service import create_service

import xmltodict


class Device(object):
    def __init__(self, data, location=None):
        self.data = xmltodict.parse(data)
        self._services = None
        self._base_url = location[:location.rfind('/')]

    def __getitem__(self, key):
        return self.data[key]

    def __str__(self):
        return self.data.__str__()

    def __repr__(self):
        return self.data.__repr__()

    @property
    def url_base(self):
        if 'URLBase' in self['root']:
            return self['root']['URLBase']
        return self._base_url

    @property
    def services(self):
        if self._services:
            return self._services

        def list_service(device):
            r = []
            slist = device.get('serviceList')
            if slist:
                slist = slist.get('service')
                slist = slist if isinstance(slist, list) else [slist]
                for s in slist:
                    r.append(create_service(self.url_base, s))
            dlist = device.get('deviceList')
            if dlist:
                dlist = dlist.get('device')
                dlist = dlist if isinstance(dlist, list) else [dlist]
                for d in dlist:
                    r += list_service(d)
            return r
        self._services = list_service(self.data['root']['device'])
        return self._services

    def find_service(self, stype):
        services = self.services
        for s in services:
            if s['serviceType'] == stype:
                yield s

    def find_first_service(self, stype):
        return next(self.find_service(stype))
