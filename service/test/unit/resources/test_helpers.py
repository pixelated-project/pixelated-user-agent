from twisted.trial import unittest
import re

from pixelated.resources import respond_json, respond_json_deferred
from test.unit.resources import DummySite
from twisted.web.test.requesthelper import DummyRequest


class TestHelpers(unittest.TestCase):

    def setUp(self):
        pass

    def test_respond_json_should_populate_response(self):
        request = DummyRequest([''])
        body = respond_json({"test": "yep"}, request)

        self.assertEqual(200, request.code)
        self.assertEqual(b"{\"test\": \"yep\"}", body)
        self.assertEqual([b"application/json"],
                         request.responseHeaders.getRawHeaders("Content-Type"))

    def test_respond_json_deferred_should_populate_response(self):
        request = DummyRequest([''])
        body = respond_json_deferred({"test": "yep"}, request)

        self.assertEqual(200, request.code)
        self.assertEqual(b"{\"test\": \"yep\"}", request.written[0])
        self.assertEqual([b"application/json"],
                         request.responseHeaders.getRawHeaders("Content-Type"))
