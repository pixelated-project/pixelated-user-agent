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
from leap.bitmask.bonafide._srp import SRPAuthError
from mock import patch
from mockito import mock, when, any as ANY
from pixelated.authentication import Authenticator, Authentication, Credentials
from twisted.internet import defer

from pixelated.application import UserAgentMode, set_up_protected_resources
from pixelated.config.services import ServicesFactory

from pixelated.config.sessions import LeapSessionFactory
import pixelated.config.services
from pixelated.resources.root_resource import RootResource
from test.support.integration import AppTestClient
from test.support.integration.app_test_client import AppTestAccount, StubSRPChecker
from test.support.test_helper import request_mock
from test.support.mockito import AnswerSelector


class MultiUserClient(AppTestClient):

    @defer.inlineCallbacks
    def start_client(self, mode=UserAgentMode(is_single_user=True)):
        self._initialize()
        self._test_account = AppTestAccount('test', self._tmp_dir.name)

        yield self._test_account.start()

        self.cleanup = lambda: self._test_account.cleanup()
        self.soledad = self._test_account.soledad

        self.service_factory = ServicesFactory(UserAgentMode(is_single_user=False))

        root_resource = RootResource(self.service_factory)
        leap_provider = mock()
        self.credentials_checker = StubSRPChecker(leap_provider)
        self.resource = set_up_protected_resources(root_resource, leap_provider, self.service_factory)

    def _mock_bonafide_auth(self, credentials):
        if credentials.username == 'username' and credentials.password == 'password':
            self.credentials_checker.add_user(credentials.username, credentials.password)
            when(Authenticator)._bonafide_auth(credentials).thenReturn(self.user_auth)
        else:
            when(Authenticator)._bonafide_auth(credentials).thenRaise(SRPAuthError)

    def login(self, username='username', password='password'):
        session = Authentication(username, 'some_user_token', 'some_user_uuid', 'session_id', {'is_admin': False})
        leap_session = self._test_account.leap_session
        leap_session.user_auth = session
        config = mock()
        config.leap_home = 'some_folder'
        leap_session.config = config
        leap_session.fresh_account = False
        self.leap_session = leap_session
        self.services = self._test_account.services
        self.user_auth = session

        credentials = Credentials(username, password)
        self._mock_bonafide_auth(credentials)

        when(LeapSessionFactory).create(username, password, session).thenReturn(leap_session)
        with patch('mockito.invocation.AnswerSelector', AnswerSelector):
            when(leap_session).initial_sync().thenAnswer(lambda: defer.succeed(None))
        when(pixelated.config.services).Services(ANY()).thenReturn(self.services)

        request = request_mock(path='/login', method="POST", body={'username': username, 'password': password})
        return self._render(request, as_json=False)

    def get(self, path, get_args='', as_json=True, from_request=None):
        request = request_mock(path)
        request.args = get_args
        if from_request:
            session = from_request.getSession()
            request.session = session
        return self._render(request, as_json)

    def post(self, path, body='', headers=None, ajax=True, csrf='token', as_json=True, from_request=None):
        headers = headers or {'Content-Type': 'application/json'}
        request = request_mock(path=path, method="POST", body=body, headers=headers, ajax=ajax, csrf=csrf)

        if from_request:
            session = from_request.getSession()
            request.session = session
        return self._render(request, as_json)
