import os
from twisted.trial import unittest

from twisted.internet import defer
from twisted.web.test.requesthelper import DummyRequest

from pixelated.resources.sandbox_resource import SandboxResource
from test.unit.resources import DummySite


class TestSandBoxResource(unittest.TestCase):
    def setUp(self):
        static_folder = os.path.dirname(os.path.abspath(__file__))
        self.resource = SandboxResource(static_folder)
        self.resource.isLeaf = True
        self.web = DummySite(self.resource)

    @defer.inlineCallbacks
    def test_render_GET_should_set_sandbox_csp_header(self):
        request = DummyRequest(['/sandbox'])
        request.method = 'GET'
        request.isSecure = lambda: True
        request.redirect = lambda _: 'irrelevant'

        expected_csp_headers = "sandbox allow-popups allow-scripts;" \
                               "default-src 'self';" \
                               "style-src *;" \
                               "script-src  *;" \
                               "font-src *;" \
                               "img-src *;" \
                               "object-src 'none';" \
                               "connect-src 'none';"

        yield self.web.get(request)

        self.assertEquals(expected_csp_headers, request.responseHeaders.getRawHeaders('X-Content-Security-Policy'.lower())[0])
        self.assertEquals(expected_csp_headers, request.responseHeaders.getRawHeaders('Content-Security-Policy'.lower())[0])
        self.assertEquals(expected_csp_headers, request.responseHeaders.getRawHeaders('X-Webkit-CSP'.lower())[0])
