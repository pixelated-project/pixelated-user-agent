#
# Copyright (c) 2015 ThoughtWorks, Inc.
#
# Pixelated is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pixelated is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Pixelated. If not, see <http://www.gnu.org/licenses/>.

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
