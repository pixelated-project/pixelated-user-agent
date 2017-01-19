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

import json
import ast
from mockito import mock, when, any as ANY
from leap.bitmask.keymanager import KeyNotFound
from leap.bitmask.keymanager.keys import OpenPGPKey

from pixelated.application import UserAgentMode
from pixelated.config.services import ServicesFactory
from pixelated.resources.keys_resource import KeysResource
import twisted.trial.unittest as unittest
from twisted.web.test.requesthelper import DummyRequest
from twisted.internet import defer
from test.unit.resources import DummySite


class TestKeysResource(unittest.TestCase):

    def setUp(self):
        self.keymanager = mock()
        self.services_factory = mock()
        self.services_factory.mode = UserAgentMode(is_single_user=True)
        self.services = mock()
        self.services.keymanager = self.keymanager
        self.services_factory._services_by_user = {'someuserid': self.keymanager}
        when(self.services_factory).services(ANY()).thenReturn(self.services)
        self.web = DummySite(KeysResource(self.services_factory))

    def test_returns_404_if_key_not_found(self):
        request = DummyRequest(['/keys'])
        request.addArg('search', 'some@inexistent.key')
        when(self.keymanager).get_key('some@inexistent.key').thenReturn(defer.fail(KeyNotFound()))

        d = self.web.get(request)

        def assert_404(_):
            self.assertEquals(404, request.code)

        d.addCallback(assert_404)
        return d

    def test_returns_the_key_as_json_if_found(self):
        request = DummyRequest(['/keys'])
        request.addArg('search', 'some@key')
        when(self.keymanager).get_key('some@key').thenReturn(defer.succeed(OpenPGPKey('some@key')))

        d = self.web.get(request)

        expected = {
            u'address': u'some@key',
            u'encr_used': False,
            u'fingerprint': u'',
            u'last_audited_at': 0,
            u'private': False,
            u'sign_used': False,
            u'tags': [u'keymanager-active'],
            u'type': u'OpenPGPKey-active',
            u'validation': u'Weak_Chain',
            u'version': 1,
        }

        def assert_response(_):
            actual = json.loads(ast.literal_eval(request.written[0]))
            self.assertEquals(expected, actual)

        d.addCallback(assert_response)
        return d

    def test_returns_unauthorized_if_key_is_private(self):
        request = DummyRequest(['/keys'])
        request.addArg('search', 'some@key')
        when(self.keymanager).get_key('some@key').thenReturn(defer.succeed(OpenPGPKey('some@key', private=True)))

        d = self.web.get(request)

        def assert_response(_):
            self.assertEquals(401, request.code)

        d.addCallback(assert_response)
        return d
