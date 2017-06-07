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
from twisted.trial import unittest
from twisted.internet.defer import inlineCallbacks

from leap.bitmask.bonafide._srp import SRPAuthError

from mock import patch, MagicMock

from pixelated.account_recovery_authenticator import AccountRecoveryAuthenticator
from pixelated.bitmask_libraries.provider import LeapProvider

PROVIDER_JSON = {
    "api_uri": "https://api.domain.org:4430",
    "api_version": "1",
    "ca_cert_fingerprint": "SHA256: some_stub_sha",
    "ca_cert_uri": "https://domain.org/ca.crt",
    "domain": "domain.org",
}


class AccountRecoveryAuthenticatorTest(unittest.TestCase):
    def setUp(self):
        self._domain = 'domain.org'
        with patch.object(LeapProvider, 'fetch_provider_json', return_value=PROVIDER_JSON):
            self._leap_provider = LeapProvider(self._domain)

    @inlineCallbacks
    def test_bonafide_srp_exceptions_should_raise_unauthorized_login(self):
        account_recovery_authenticator = AccountRecoveryAuthenticator(self._leap_provider)
        mock_bonafide_session = MagicMock()
        mock_bonafide_session.authenticate = MagicMock(side_effect=SRPAuthError())
        with patch('pixelated.authentication.Session', return_value=mock_bonafide_session):
            with self.assertRaises(UnauthorizedLogin):
                try:
                    yield account_recovery_authenticator.authenticate('username', 'recovery_code')
                except UnauthorizedLogin as e:
                    self.assertEqual("User typed wrong username/recovery-code combination.", e.message)
                    raise

    def test_bonafide_auth_called_with_recovery_as_true(self):
        auth = AccountRecoveryAuthenticator(self._leap_provider)
        mock_bonafide_session = MagicMock()

        with patch('pixelated.authentication.Session', return_value=mock_bonafide_session):
            auth.authenticate('username', 'password')
            mock_bonafide_session.authenticate.assert_called_with(recovery=True)
