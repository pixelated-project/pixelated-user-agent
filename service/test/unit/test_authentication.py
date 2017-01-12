from twisted.cred.error import UnauthorizedLogin
from twisted.internet.defer import inlineCallbacks
from twisted.trial import unittest

from leap.bitmask.bonafide._srp import SRPAuthError

from mock import patch, Mock

from pixelated.authentication import Authenticator
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
                    self.assertEqual("User typed wrong password/username combination.", e.message)
                    raise

    @inlineCallbacks
    def test_domain_name_is_stripped_before_making_bonafide_srp_auth(self):
        username_without_domain = 'username'
        username_with_domain = '%s@%s' % (username_without_domain, self._domain)
        auth = Authenticator(self._leap_provider)
        with patch.object(Authenticator, '_bonafide_auth') as mock_leap_authenticate:
            yield auth.authenticate(username_with_domain, 'password')
            mock_leap_authenticate.assert_called_once_with(username_without_domain, 'password')

    @inlineCallbacks
    def test_successful_bonafide_auth_should_return_the_user_authentication_object(self):
        auth = Authenticator(self._leap_provider)
        mock_bonafide_session = Mock()
        mock_srp_auth = Mock()
        mock_srp_auth.token = 'some_token'
        mock_srp_auth.uuid = 'some_uuid'
        mock_bonafide_session.authenticate = Mock(return_value=mock_srp_auth)
        with patch('pixelated.authentication.Session', return_value=mock_srp_auth):
            resulting_auth = yield auth.authenticate('username@domain.org', 'password')
            self.assertIsInstance(resulting_auth, Authentication)
            self.assertEquals('username', resulting_auth.username)
            self.assertEquals('some_token', resulting_auth.token)
            self.assertEquals('some_uuid', resulting_auth.uuid)

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
