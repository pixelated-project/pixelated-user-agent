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
import json

from mockito import verify
from mockito import when
from twisted.internet import defer

from test.support.integration.soledad_test_base import MultiUserSoledadTestBase


class UsersResourceTest(MultiUserSoledadTestBase):

    @defer.inlineCallbacks
    def wait_for_session_user_id_to_finish(self):
        yield self.adaptor.initialize_store(self.app_test_client.soledad)

    @defer.inlineCallbacks
    def test_online_users_count_uses_leap_auth_privileges(self):

        response, login_request = yield self.app_test_client.login()
        yield response

        yield self.wait_for_session_user_id_to_finish()

        when(self.app_test_client.user_auth).is_admin().thenReturn(True)
        response, request = self.app_test_client.get(
            "/users",
            json.dumps({'csrftoken': [login_request.getCookie('XSRF-TOKEN')]}),
            from_request=login_request,
            as_json=False)
        yield response

        self.assertEqual(200, request.code)     # redirected
        self.assertEqual('{"count": 1}', request.getWrittenData())     # redirected
        verify(self.app_test_client.user_auth).is_admin()
