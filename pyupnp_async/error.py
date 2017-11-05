import xmltodict


class UpnpSoapError(Exception):
    def __init__(self, xmlstr):
        self.xml = xmlstr
        self.data = xmltodict.parse(xmlstr)

        detail = self.data['s:Envelope']['s:Body']['s:Fault']['detail']
        self.error_code = int(detail['UPnPError']['errorCode'])

    def __str__(self):
        return self.xml
