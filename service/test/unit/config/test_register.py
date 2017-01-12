from twisted.trial import unittest

from mock import patch, Mock
from pixelated.register import validate_username, validate_password, _set_provider, register
from twisted.internet import defer
from twisted.internet.defer import inlineCallbacks


class TestRegister(unittest.TestCase):

    def test_username_raises_error_when_it_contains_uppercase_letters(self):
        with self.assertRaises(ValueError):
            validate_username('INVALIDUSERNAME')

    def test_username_raises_error_when_it_contains_special_characters(self):
        with self.assertRaises(ValueError):
            validate_username('invalid@username')

    def test_password_raises_error_if_shorter_than_8_characters(self):
        with self.assertRaises(ValueError):
            validate_password('short')

    def test_username_pass_when_valid(self):
        try:
            validate_username('a.valid_username-123')
        except:
            self.fail('Valid username should not raise an exception')

    def test_sets_provider(self):
        mock_provider = Mock()
        with patch('pixelated.register.LeapProvider', return_value=mock_provider) as mock_instantiate_provider:
            provider = _set_provider('mocked_provider_cert', 'mocked_provider_cert_fingerprint', 'mocked_server_name')
            mock_instantiate_provider.assert_called_once_with('mocked_server_name')
            self.assertEqual(provider, mock_provider)
            self.assertTrue(mock_provider.setup_ca.called)
            self.assertTrue(mock_provider.download_settings.called)

    @patch('pixelated.register.logger')
    @inlineCallbacks
    def test_register_uses_bonafide_auth(self, mock_logger):
        mock_provider = Mock()
        mock_provider.api_uri = 'https://pro.vi.der'
        mock_bonafide_session = Mock()
        mock_bonafide_session.signup.return_value = defer.succeed(('created', 'user'))
        with patch('pixelated.register.Session', return_value=mock_bonafide_session) as mock_instantiate_bonafide_session:
            yield register('username', 'password', mock_provider, 'invite')
            mock_instantiate_bonafide_session.assert_called_once()
            mock_bonafide_session.signup.assert_called_once_with('username', 'password', 'invite')
            mock_logger.info.assert_called_with('User username successfully registered')
