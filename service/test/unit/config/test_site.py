from twisted.trial import unittest
from mock import MagicMock
from pixelated.config.site import PixelatedSite
from twisted.protocols.basic import LineReceiver


class TestPixelatedSite(unittest.TestCase):

    def test_add_security_headers(self):
        request = self.create_request()
        request.process()

        header_value = "default-src 'self'; style-src 'self' 'unsafe-inline'"
        self.assertEquals(header_value, request.responseHeaders.getRawHeaders('X-Content-Security-Policy'.lower())[0])
        self.assertEquals(header_value, request.responseHeaders.getRawHeaders('Content-Security-Policy'.lower())[0])
        self.assertEquals(header_value, request.responseHeaders.getRawHeaders('X-Webkit-CSP'.lower())[0])

        self.assertEqual('SAMEORIGIN', request.responseHeaders.getRawHeaders('X-Frame-Options'.lower())[0])
        self.assertEqual('1; mode=block', request.responseHeaders.getRawHeaders('X-XSS-Protection'.lower())[0])
        self.assertEqual('nosniff', request.responseHeaders.getRawHeaders('X-Content-Type-Options'.lower())[0])

    def test_add_strict_transport_security_header_if_secure(self):
        request = self.create_request()
        request._forceSSL = True

        request.process()

        self.assertTrue(request.responseHeaders.hasHeader('Strict-Transport-Security'.lower()))
        self.assertEqual('max-age=31536000; includeSubDomains', request.responseHeaders.getRawHeaders('Strict-Transport-Security'.lower())[0])

    def test_does_not_add_strict_transport_security_header_if_plain_http(self):
        request = self.create_request()

        request.process()

        self.assertFalse(request.responseHeaders.hasHeader('Strict-Transport-Security'.lower()))

    def create_request(self):
        channel = LineReceiver()
        channel.site = PixelatedSite(MagicMock())
        request = PixelatedSite.requestFactory(channel=channel, queued=True)
        request.method = "GET"
        request.uri = "localhost"
        request.clientproto = 'HTTP/1.1'
        request.prepath = []
        request.postpath = request.uri.split('/')[1:]
        request.path = "/"
        return request
