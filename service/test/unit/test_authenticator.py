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

from twisted.cred.error import UnauthorizedLogin
from twisted.internet.defer import inlineCallbacks
from twisted.trial import unittest

from leap.bitmask.bonafide._srp import SRPAuthError

from mock import patch, Mock

from pixelated.authentication import Authenticator, Credentials
from pixelated.bitmask_libraries.provider import LeapProvider
from pixelated.authentication import Authentication

PROVIDER_JSON = {
    "api_uri": "https://api.domain.org:4430",
    "api_version": "1",
    "ca_cert_fingerprint": "SHA256: some_stub_sha",
    "ca_cert_uri": "https://domain.org/ca.crt",
    "domain": "domain.org",
}


class AuthenticatorTest(unittest.TestCase):
    def setUp(self):
        self._domain = 'domain.org'
        with patch.object(LeapProvider, 'fetch_provider_json', return_value=PROVIDER_JSON):
            self._leap_provider = LeapProvider(self._domain)

    @inlineCallbacks
    def test_bonafide_srp_exceptions_should_raise_unauthorized_login(self):
        auth = Authenticator(self._leap_provider)
        mock_bonafide_session = Mock()
        mock_bonafide_session.authenticate = Mock(side_effect=SRPAuthError())
        with patch('pixelated.authentication.Session', return_value=mock_bonafide_session):
            with self.assertRaises(UnauthorizedLogin):
                try:
                    yield auth.authenticate('username', 'password')
                except UnauthorizedLogin as e:
                    self.assertEqual("User typed wrong username/password combination.", e.message)
                    raise

    @inlineCallbacks
    def test_domain_name_is_stripped_before_making_bonafide_srp_auth(self):
        username_without_domain = 'username'
        username_with_domain = '%s@%s' % (username_without_domain, self._domain)
        credentials = Credentials(username_without_domain, 'password')
        auth = Authenticator(self._leap_provider)
        with patch.object(Authenticator, '_bonafide_auth') as mock_leap_authenticate:
            yield auth.authenticate(username_with_domain, 'password')
            mock_leap_authenticate.assert_called_once_with(credentials)

    @inlineCallbacks
    def test_successful_bonafide_auth_should_return_the_user_authentication_object(self):
        auth = Authenticator(self._leap_provider)
        mock_bonafide_session = Mock()
        mock_bonafide_session.token = 'some_token'
        mock_bonafide_session.uuid = 'some_uuid'

        with patch('pixelated.authentication.Session', return_value=mock_bonafide_session):
            resulting_auth = yield auth.authenticate('username@domain.org', 'password')
            self.assertIsInstance(resulting_auth, Authentication)
            self.assertEquals('username', resulting_auth.username)
            self.assertEquals('some_token', resulting_auth.token)
            self.assertEquals('some_uuid', resulting_auth.uuid)
            self.assertEquals(mock_bonafide_session, auth.bonafide_session)

    def test_bonafide_auth_called_with_recovery_as_false(self):
        auth = Authenticator(self._leap_provider)
        mock_bonafide_session = Mock()

        with patch('pixelated.authentication.Session', return_value=mock_bonafide_session):
            auth.authenticate('username', 'password')
            mock_bonafide_session.authenticate.assert_called_with(recovery=False)

    def test_username_without_domain_is_not_changed(self):
        username_without_domain = 'username'
        auth = Authenticator(self._leap_provider)
        self.assertEqual(username_without_domain, auth.clean_username(username_without_domain))

    def test_username_with_domain_is_stripped(self):
        username_without_domain = 'username'
        username_with_domain = '%s@%s' % (username_without_domain, self._domain)
        auth = Authenticator(self._leap_provider)
        self.assertEqual(username_without_domain, auth.clean_username(username_with_domain))

    def test_username_with_wrong_domain_raises_exception(self):
        username_without_domain = 'username'
        username_with_wrong_domain = '%s@%s' % (username_without_domain, 'wrongdomain.org')
        auth = Authenticator(self._leap_provider)
        with self.assertRaises(UnauthorizedLogin):
            try:
                auth.clean_username(username_with_wrong_domain)
            except UnauthorizedLogin as e:
                self.assertEqual("User typed a wrong domain.", e.message)
                raise

    def test_username_with_domain(self):
        auth = Authenticator(self._leap_provider)
        self.assertEqual('user@domain.org', auth.username_with_domain('user'))

    def test_extract_username_extracts_from_plain_username(self):
        auth = Authenticator(self._leap_provider)
        self.assertEqual(auth.extract_username('user'), 'user')

    def test_extract_username_extracts_from_email_address(self):
        auth = Authenticator(self._leap_provider)
        self.assertEqual(auth.extract_username('user@domain.org'), 'user')
