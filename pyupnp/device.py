from .service import Service

import xmltodict


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
