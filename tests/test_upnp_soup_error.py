from .context import UpnpSoapError

import unittest


XML_STR = '''
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
<s:Body>
<s:Fault>
<faultcode>s:Client</faultcode>
<faultstring>UPnPError</faultstring>
<detail>
<UPnPError xmlns="urn:schemas-upnp-org:control-1-0">
<errorCode>718</errorCode>
<errorDescription>ConflictinMappingEntry</errorDescription></UPnPError>
</detail>
</s:Fault>
</s:Body>
</s:Envelope>
'''


class UpnpSoapErrorTests(unittest.TestCase):
    def test_should_parse_error_xml(self):
        sut = UpnpSoapError(XML_STR)

        self.assertEqual(718, sut.error_code)
