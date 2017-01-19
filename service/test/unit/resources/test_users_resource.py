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

from mockito import mock, when, verify
from twisted.trial import unittest
from twisted.web.test.requesthelper import DummyRequest

from pixelated.config.services import Services, ServicesFactory
from pixelated.resources.users import UsersResource
from test.unit.resources import DummySite


class TestUsersResource(unittest.TestCase):

    def setUp(self):
        self.services_factory = mock()
        self.resource = UsersResource(self.services_factory)
        self.web = DummySite(self.resource)

    def test_numbers_of_users_online(self):
        number_of_users_online = 6
        self.services_factory.online_sessions = lambda: number_of_users_online
        self.resource.is_admin = lambda _: True
        request = DummyRequest([''])

        d = self.web.get(request)

        def assert_users_count(_):
            self.assertEqual(200, request.code)
            self.assertEqual('{"count": %d}' % number_of_users_online, request.written[0])

        d.addCallback(assert_users_count)
        return d

    def test_numbers_of_users_online_is_only_available_only_for_admin(self):
        self.resource.is_admin = lambda _: False
        request = DummyRequest([''])
        d = self.web.get(request)

        def assert_is_forbidden(_):
            self.assertEqual(401, request.responseCode)
            self.assertEqual('Unauthorized!', request.written[0])

        d.addCallback(assert_is_forbidden)
        return d

    def test_is_admin_is_queried_from_leap_auth(self):
        leap_session = mock()
        auth = mock()
        auth.uuid = 'some_id1'
        leap_session.user_auth = auth
        leap_session.config = mock()
        services = Services(leap_session)
        service_factory = ServicesFactory(mock())
        service_factory.add_session('some_id1', services)

        when(auth).is_admin().thenReturn(True)
        request = mock()
        resource = UsersResource(service_factory)

        when(resource)._get_user_id_from_request(request).thenReturn('some_id1')

        self.assertTrue(resource.is_admin(request))
        verify(auth).is_admin()
