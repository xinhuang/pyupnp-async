import xmltodict

class UpnpError(Exception):
    pass

class UpnpSoapError(UpnpError):
    def __init__(self, xmlstr):
        self.xml = xmlstr
        self.data = xmltodict.parse(xmlstr)

        detail = self.data['s:Envelope']['s:Body']['s:Fault']['detail']
        self.error_code = int(detail['UPnPError']['errorCode'])

    def __str__(self):
        return self.xml

class UpnpKeyError(UpnpError):
    def __init__(self, xmlstr, key):
        self.xml = xmlstr
        self.keyError = key

    def __str__(self):
        return "{} missing in {}".format(self.keyError, self.xml)
