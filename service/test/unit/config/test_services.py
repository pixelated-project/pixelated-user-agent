#
# Copyright (c) 2014 ThoughtWorks, Inc.
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

from mock import Mock, ANY, patch
from mockito import mock, verify

from pixelated.config.services import Services, ServicesFactory


class ServicesTest(unittest.TestCase):

    def setUp(self):
        super(ServicesTest, self).setUp()
        self.leap_session = mock()
        config = mock()
        self.leap_session.config = config
        self.services = Services(self.leap_session)

    def test_close_services_closes_the_underlying_leap_session(self):
        self.services.close()
        verify(self.leap_session).close()


class ServicesFactoryTest(unittest.TestCase):

    def setUp(self):
        self.service_factory = ServicesFactory(Mock())

    def test_users_has_no_default_sessions(self):
        user_id = ANY
        self.assertFalse(self.service_factory.has_session(user_id))

    def test_add_user_sessions(self):
        user_id = 'irrelevant'
        some_service = Mock()

        self.service_factory.add_session(user_id, some_service)

        self.assertTrue(self.service_factory.has_session(user_id))
        self.assertEqual(some_service, self.service_factory.services(user_id))

    def test_online_sessions_counts_logged_in_users(self):
        self.service_factory.add_session('some_id1', mock())
        self.service_factory.add_session('some_id2', mock())

        self.assertEqual(2, self.service_factory.online_sessions())

    @patch('pixelated.config.services.Services.setup')
    def test_create_services_from_leap_session_sets_up_services_and_add_a_user_session(self, mock_setup_services):
        leap_session = Mock()
        user_id = 'irrelevant'
        leap_session.user_auth.uuid = user_id

        self.service_factory.create_services_from(leap_session)

        self.assertTrue(mock_setup_services.called)
        self.assertTrue(self.service_factory.has_session(user_id))

    def test_destroy_session_using_close_user_services_and_deletes_sessions(self):
        user_id = 'irrelevant'
        some_service = Mock()
        self.service_factory.add_session(user_id, some_service)

        self.service_factory.destroy_session(user_id)

        self.assertFalse(self.service_factory.has_session(user_id))
        self.assertTrue(some_service.close.called)

    def test_sessions_can_be_destroyed_using_email_rather_than_uuid(self):
        user_id = 'irrelevant'
        username = 'haha'
        email = '%s@ha.ha' % username
        some_service = Mock()
        self.service_factory.add_session(user_id, some_service)
        self.service_factory.map_email(username, user_id)

        self.service_factory.destroy_session(email, using_email=True)

        self.assertFalse(self.service_factory.has_session(user_id))
        self.assertTrue(some_service.close.called)
