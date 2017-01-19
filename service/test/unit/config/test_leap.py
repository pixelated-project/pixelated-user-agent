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

from leap.soledad.common.errors import InvalidAuthTokenError
from mock import MagicMock, patch, Mock
from twisted.trial import unittest
from twisted.internet import defer
from pixelated.config.leap import create_leap_session, BootstrapUserServices, initialize_leap_single_user
from pixelated.config.sessions import LeapSessionFactory, SessionCache, SoledadWrongPassphraseException
from leap.soledad.common.crypto import UnknownMacMethodError


class TestLeapInit(unittest.TestCase):

    @patch('pixelated.config.sessions.SessionCache.session_key')
    @defer.inlineCallbacks
    def test_create_leap_session_calls_initial_sync_and_caches_sessions(self, mock_session_key):
        mock_session_key.return_value = 'mocked key'
        provider_mock = MagicMock()
        auth_mock = MagicMock()
        session = MagicMock()
        with patch.object(LeapSessionFactory, '_create_new_session', return_value=session):
            yield create_leap_session(provider_mock, 'username', 'password', auth=auth_mock)

        session.first_required_sync.assert_called_once()
        self.assertEqual({'mocked key': session}, SessionCache.sessions)

    @patch('pixelated.config.sessions.SessionCache.lookup_session')
    @defer.inlineCallbacks
    def test_create_leap_session_uses_caches_when_available_and_not_sync(self, mock_cache_lookup_session):
        mock_cache_lookup_session.return_value = 'mocked key'
        provider_mock = MagicMock()
        auth_mock = MagicMock()
        session = MagicMock()
        mock_cache_lookup_session.return_value = session

        with patch.object(LeapSessionFactory, '_create_new_session', return_value=session):
            returned_session = yield create_leap_session(provider_mock, 'username', 'password', auth=auth_mock)

        self.assertFalse(session.first_required_sync.called)
        self.assertEqual(session, returned_session)

    @patch('pixelated.config.leap.initialize_leap_provider')
    @patch('pixelated.config.leap.credentials')
    @patch('pixelated.config.leap.events_server')
    @defer.inlineCallbacks
    def test_init_single_user_does_bonafide_auth_and_gives_a_leap_session(self, mock_event_server, mock_credentials, mock_init_leap_provider):
        provider_mock = MagicMock()
        mock_init_leap_provider.return_value = provider_mock
        mock_credentials.read.return_value = ('provider_url', 'username', 'password')
        mock_authenticator = MagicMock()

        with patch('pixelated.config.leap.Authenticator', return_value=mock_authenticator) as mock_instantiate_authenticator:
            auth_mock = MagicMock()
            mock_authenticator.authenticate.return_value = defer.succeed(auth_mock)
            leap_session = MagicMock()
            deferred_leap_session = defer.succeed(leap_session)
            with patch.object(LeapSessionFactory, 'create', return_value=deferred_leap_session) as mock_create_leap_session:
                returned_session = yield initialize_leap_single_user('leap_provider_cert', 'leap_provider_cert_fingerprint', 'credentials_file', 'leap_home')

        mock_event_server.ensure_server.assert_called_once()
        mock_credentials.read.assert_called_once_with('credentials_file')
        mock_init_leap_provider.asser_called_once_with('provider_url', 'leap_provider_cert', 'leap_provider_cert_fingerprint', 'leap_home')
        mock_instantiate_authenticator.assert_called_once_with(provider_mock)
        mock_authenticator.authenticate.assert_called_once_with('username', 'password')
        mock_create_leap_session.assert_called_once_with('username', 'password', auth_mock)
        self.assertEqual(leap_session, returned_session)


class TestUserBootstrap(unittest.TestCase):

    def setUp(self):
        self._service_factory = Mock()
        self._provider = Mock()
        self._user_bootstrap = BootstrapUserServices(self._service_factory, self._provider)

        username = 'ayoyo'
        password = 'ayoyo_password'
        self.username = username
        self.password = password

        user_auth = Mock()
        user_auth.username = username
        self.uuid = 'some_user_uuid'
        user_auth.uuid = self.uuid
        self.user_auth = user_auth

        leap_session = Mock()
        leap_session.user_auth = user_auth
        leap_session.fresh_account = False
        self.leap_session = leap_session

    @patch('pixelated.config.leap.create_leap_session')
    def test_should_create_leap_session(self, mock_create_leap_session):
        mock_create_leap_session.return_value = self.leap_session
        self._service_factory.has_session.return_value = False

        self._user_bootstrap.setup(self.user_auth, self.password)

        mock_create_leap_session.called_once_with(self._provider, self.username, self.password, self.user_auth)

    @patch('pixelated.config.leap.create_leap_session')
    def test_should_setup_user_services_and_map_email(self, mock_create_leap_session):
        mock_create_leap_session.return_value = self.leap_session
        self._service_factory.has_session.return_value = False

        self._user_bootstrap.setup(self.user_auth, self.password)

        self._service_factory.create_services_from.assert_called_once_with(self.leap_session)
        self._service_factory.map_email.assert_called_once_with(self.username, self.uuid)

    @patch('pixelated.config.leap.create_leap_session')
    def test_should_not_user_services_if_there_is_already_a_session(self, mock_create_leap_session):
        mock_create_leap_session.return_value = self.leap_session
        self._service_factory.has_session.return_value = True

        self._user_bootstrap.setup(self.user_auth, self.password)

        self.assertFalse(self._service_factory.create_services_from.called)

    @patch('pixelated.config.leap.add_welcome_mail')
    @patch('pixelated.config.leap.create_leap_session')
    def test_should_add_welcome_email_on_a_fresh_account(self, mock_create_leap_session, mock_add_welcome_email):
        self.leap_session.fresh_account = True
        mail_store = Mock()
        self.leap_session.mail_store = mail_store
        mock_create_leap_session.return_value = self.leap_session
        self._service_factory.has_session.return_value = False
        default_language = 'pt-BR'

        self._user_bootstrap.setup(self.user_auth, self.password)

        mock_add_welcome_email.assert_called_once_with(mail_store, default_language)

    @patch('pixelated.config.leap.create_leap_session')
    @patch('pixelated.config.leap.log.warn')
    @defer.inlineCallbacks
    def test__setup__should_log_an_error_raised_from_create_leap_session(self, mock_logger_warn, mock_create_leap_session):
        mock_create_leap_session.side_effect = SoledadWrongPassphraseException(UnknownMacMethodError("oh no"))
        with self.assertRaises(SoledadWrongPassphraseException):
            yield self._user_bootstrap.setup(self.user_auth, self.password, '')
        mock_logger_warn.assert_called_once_with("SoledadWrongPassphraseException: oh no. Closing session for user: ayoyo")

    @patch('pixelated.config.leap.BootstrapUserServices._setup_user_services')
    @patch('pixelated.config.leap.create_leap_session')
    @patch('pixelated.config.leap.log.warn')
    @defer.inlineCallbacks
    def test__setup__should_log_an_error_raised_from__setup_user_services(self, mock_logger_warn, mock_create_leap_session, mock_setup_user_services):
        leap_session = Mock()
        mock_create_leap_session.return_value = leap_session
        mock_setup_user_services.side_effect = UnknownMacMethodError("oh no")
        with self.assertRaises(UnknownMacMethodError):
            yield self._user_bootstrap.setup(self.user_auth, self.password, '')
        mock_logger_warn.assert_called_once_with("UnknownMacMethodError: oh no. Closing session for user: ayoyo")

    @patch('pixelated.config.leap.BootstrapUserServices._setup_user_services')
    @patch('pixelated.config.leap.create_leap_session')
    @patch('pixelated.config.leap.log.warn')
    @defer.inlineCallbacks
    def test__setup__should_close_leap_sesson_on_error_from__setup_user_services(self, mock_logger_warn, mock_create_leap_session, mock_setup_user_services):
        leap_session = Mock()
        leap_session.close = Mock()
        mock_create_leap_session.return_value = leap_session
        mock_setup_user_services.side_effect = UnknownMacMethodError("oh no")
        with self.assertRaises(UnknownMacMethodError):
            yield self._user_bootstrap.setup(self.user_auth, self.password, '')
        leap_session.close.assert_called_once_with()

    @patch('pixelated.config.leap.BootstrapUserServices._add_welcome_email')
    @patch('pixelated.config.leap.BootstrapUserServices._setup_user_services')
    @patch('pixelated.config.leap.create_leap_session')
    @patch('pixelated.config.leap.log.warn')
    @defer.inlineCallbacks
    def test__setup__should_close_leap_sesson_on_error_from__add_welcome_email(self, mock_logger_warn, mock_create_leap_session, _, mock_add_welcome_email):
        leap_session = Mock()
        leap_session.close = Mock()
        mock_create_leap_session.return_value = leap_session
        mock_add_welcome_email.side_effect = UnknownMacMethodError("oh no")
        with self.assertRaises(UnknownMacMethodError):
            yield self._user_bootstrap.setup(self.user_auth, self.password, '')
        leap_session.close.assert_called_once_with()
