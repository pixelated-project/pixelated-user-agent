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
from twisted.internet import defer

from test.support.integration.soledad_test_base import MultiUserSoledadTestBase


class MultiUserLogoutTest(MultiUserSoledadTestBase):

    @defer.inlineCallbacks
    def wait_for_session_user_id_to_finish(self):
        yield self.adaptor.initialize_store(self.app_test_client.soledad)

    @defer.inlineCallbacks
    def test_logout_deletes_services_stop_background_reactor_tasks_and_closes_soledad(self):
        response, login_request = yield self.app_test_client.login()
        yield response

        yield self.wait_for_session_user_id_to_finish()

        response, request = self.app_test_client.post(
            "/logout",
            json.dumps({'csrftoken': [login_request.getCookie('XSRF-TOKEN')]}),
            from_request=login_request,
            as_json=False)
        yield response

        self.assertEqual(302, request.responseCode)     # redirected
        verify(self.app_test_client.services).close()
