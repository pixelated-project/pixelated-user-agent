#
# Copyright (c) 2017 ThoughtWorks, Inc.
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

from mock import MagicMock, patch

from twisted.internet import defer
from twisted.trial import unittest
from twisted.web.test.requesthelper import DummyRequest
from twisted.cred.error import UnauthorizedLogin

from pixelated.resources.account_recovery_resource import AccountRecoveryResource
from test.unit.resources import DummySite


class TestAccountRecoveryResource(unittest.TestCase):
    def setUp(self):
        self.services_factory = MagicMock()
        self.provider = MagicMock()
        self.resource = AccountRecoveryResource(self.services_factory, self.provider)
        self.web = DummySite(self.resource)

    def test_get(self):
        request = DummyRequest(['/account-recovery'])
        request.method = 'GET'
        d = self.web.get(request)

        def assert_200_when_user_logged_in(_):
            self.assertEqual(200, request.responseCode)
            self.assertIn("DOCTYPE html", request.written[0])

        d.addCallback(assert_200_when_user_logged_in)
        return d

    @patch('pixelated.resources.account_recovery_resource.AccountRecoveryAuthenticator.authenticate')
    def test_post_returns_successfully(self, mock_authenticate):
        request = DummyRequest(['/account-recovery'])
        request.method = 'POST'
        request.content = MagicMock()
        request.content.getvalue.return_value = '{"username": "alice", "userCode": "abc123", "password": "12345678", "confirmPassword": "12345678"}'
        mock_authenticate.return_value = defer.succeed('')

        d = self.web.get(request)

        def assert_successful_response(_):
            self.assertEqual(200, request.responseCode)
            mock_authenticate.assert_called_with('alice', 'abc123')

        d.addCallback(assert_successful_response)
        return d

    @patch('pixelated.resources.account_recovery_resource.AccountRecoveryAuthenticator.authenticate')
    def test_post_returns_unauthorized(self, mock_authenticate):
        request = DummyRequest(['/account-recovery'])
        request.method = 'POST'
        request.content = MagicMock()
        request.content.getvalue.return_value = '{"username": "alice", "userCode": "abc123", "password": "12345678", "confirmPassword": "12345678"}'
        mock_authenticate.return_value = defer.fail(UnauthorizedLogin())

        d = self.web.get(request)

        def assert_error_response(_):
            self.assertEqual(401, request.responseCode)
            mock_authenticate.assert_called_with('alice', 'abc123')

        d.addErrback(assert_error_response)
        return d

    def test_post_returns_failure_by_empty_usercode(self):
        request = DummyRequest(['/account-recovery'])
        request.method = 'POST'
        request.content = MagicMock()
        request.content.getvalue.return_value = '{"username": "alice", "userCode": "", "password": "1234", "confirmPassword": "1234"}'

        d = self.web.get(request)

        def assert_error_response(_):
            self.assertEqual(400, request.responseCode)

        d.addCallback(assert_error_response)
        return d

    def test_post_returns_failure_by_password_length(self):
        request = DummyRequest(['/account-recovery'])
        request.method = 'POST'
        request.content = MagicMock()
        request.content.getvalue.return_value = '{"username": "alice", "userCode": "abc123", "password": "1234", "confirmPassword": "1234"}'

        d = self.web.get(request)

        def assert_error_response(_):
            self.assertEqual(400, request.responseCode)

        d.addCallback(assert_error_response)
        return d

    def test_post_returns_failure_by_password_confirmation(self):
        request = DummyRequest(['/account-recovery'])
        request.method = 'POST'
        request.content = MagicMock()
        request.content.getvalue.return_value = '{"username": "alice", "userCode": "abc123", "password": "12345678", "confirmPassword": "1234"}'

        d = self.web.get(request)

        def assert_error_response(_):
            self.assertEqual(400, request.responseCode)

        d.addCallback(assert_error_response)
        return d
