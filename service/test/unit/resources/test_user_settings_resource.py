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
import json
import ast

from pixelated.application import UserAgentMode
from pixelated.resources.user_settings_resource import UserSettingsResource, FINGERPRINT_NOT_FOUND
from mockito import mock, when, any
from test.unit.resources import DummySite
from twisted.web.test.requesthelper import DummyRequest
from leap.bitmask.keymanager.keys import OpenPGPKey
from twisted.internet import defer
from twisted.python.failure import Failure

MAIL_ADDRESS = 'some@key'
FINGERPRINT = '4-8-12-13-23-42'


class TestUserSettingsResource(unittest.TestCase):

    def setUp(self):
        self.services = mock()
        self.mail_service = mock()
        self.mail_service.account_email = MAIL_ADDRESS
        self.keymanager = mock()
        self.services_factory = mock()
        self.services_factory.mode = UserAgentMode(is_single_user=True)
        self.services.mail_service = self.mail_service
        self.services.keymanager = self.keymanager
        self.services_factory._services_by_user = {'someuserid': self.keymanager}
        self.resource = UserSettingsResource(self.services_factory)
        when(self.services_factory).services(any()).thenReturn(self.services)
        self.web = DummySite(self.resource)

    def test_fingerprint_given(self):
        key = OpenPGPKey(MAIL_ADDRESS)
        key.fingerprint = FINGERPRINT
        request = DummyRequest(['/user-settings'])
        when(self.keymanager).get_key(MAIL_ADDRESS).thenReturn(defer.succeed(key))

        d = self.web.get(request)

        def assert_response(_):
            response = json.loads(request.written[0])
            self.assertEqual(FINGERPRINT, response['fingerprint'])
            self.assertEqual(MAIL_ADDRESS, response['account_email'])

        d.addCallback(assert_response)
        return d

    def test_fingerprint_missing(self):
        key = OpenPGPKey(MAIL_ADDRESS)
        key.fingerprint = FINGERPRINT
        request = DummyRequest(['/user-settings'])
        when(self.keymanager).get_key(MAIL_ADDRESS).thenReturn(defer.fail(Failure))

        d = self.web.get(request)

        def assert_response(_):
            response = json.loads(request.written[0])
            self.assertEqual(FINGERPRINT_NOT_FOUND, response['fingerprint'])
            self.assertEqual(MAIL_ADDRESS, response['account_email'])

        d.addCallback(assert_response)
        return d
