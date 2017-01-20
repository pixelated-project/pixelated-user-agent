# -*- encoding:utf-8 -*-
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

from mock import patch
from mock import MagicMock
from mockito import when
from twisted.internet import defer
from pixelated.config.sessions import LeapSession, SessionCache, LeapSessionFactory, SoledadWrongPassphraseException
from pixelated.bitmask_libraries.keymanager import UploadKeyError
from test.unit.bitmask_libraries.test_abstract_leap import AbstractLeapTest
from leap.common.events.catalog import KEYMANAGER_FINISHED_KEY_GENERATION
from leap.soledad.common.crypto import WrongMacError, UnknownMacMethodError


class SessionTest(AbstractLeapTest):

    def setUp(self):
        super(SessionTest, self).setUp()
        self.smtp_mock = MagicMock()

    @patch('pixelated.config.sessions.register')
    @patch('pixelated.config.sessions.Account')
    @defer.inlineCallbacks
    def test_background_jobs_are_started_during_initial_sync(self, *unused):
        mail_fetcher_mock = MagicMock()
        with patch('pixelated.config.sessions.reactor.callFromThread', new=_execute_func) as _:
            with patch.object(LeapSession, '_create_incoming_mail_fetcher', return_value=mail_fetcher_mock) as _:
                session = self._create_session()
                yield session.first_required_sync()
                mail_fetcher_mock.startService.assert_called_once()

    @patch('pixelated.config.sessions.register')
    @defer.inlineCallbacks
    def test_upload_key_error_closes_the_session(self, _):
        when(self.keymanager).generate_openpgp_key().thenRaise(UploadKeyError('Could not upload key'))
        session = self._create_session()
        session.close = MagicMock()

        with self.assertRaises(UploadKeyError):
            yield session.finish_bootstrap()
            session.close.assert_called_once()

    @patch('pixelated.config.sessions.register')
    @patch('pixelated.config.sessions.unregister')
    @patch('pixelated.config.sessions.Account')
    @defer.inlineCallbacks
    def test_that_close_stops_background_jobs(self, *unused):
        mail_fetcher_mock = MagicMock()
        with patch('pixelated.config.sessions.reactor.callFromThread', new=_execute_func) as _:
            with patch.object(LeapSession, '_create_incoming_mail_fetcher', return_value=mail_fetcher_mock) as _:
                session = self._create_session()
                yield session.first_required_sync()
                session.close()
                mail_fetcher_mock.stopService.assert_called_once()

    @patch('pixelated.config.sessions.register')
    @defer.inlineCallbacks
    def test_that_sync_defers_to_soledad(self, *unused):
        session = self._create_session()
        yield session.sync()
        self.soledad_session.sync.assert_called_once()

    @patch('pixelated.config.sessions.register')
    def test_session_registers_to_generated_keys(self, register_mock):
        email = 'someone@somedomain.tld'
        self.provider.address_for.return_value = email
        session = self._create_session()
        register_mock.assert_called_once_with(KEYMANAGER_FINISHED_KEY_GENERATION, session._set_fresh_account, uid=email, replace=True)

    @patch('pixelated.config.sessions.register')
    def test_close_unregisters_from_generate_keys_events(self, _):
        email = 'someone@somedomain.tld'
        self.provider.address_for.return_value = email
        session = self._create_session()

        with patch('pixelated.config.sessions.unregister') as unregister_mock:
            session.close()

            unregister_mock.assert_called_once_with(KEYMANAGER_FINISHED_KEY_GENERATION, uid=email)

    @patch('pixelated.config.sessions.register')
    def test_close_stops_soledad(self, _):
        email = 'someone@somedomain.tld'
        self.provider.address_for.return_value = email
        session = self._create_session()

        with patch('pixelated.config.sessions.unregister') as unregister_mock:
            session.close()

        self.soledad_session.close.assert_called_once_with()

    @patch('pixelated.config.sessions.register')
    def test_close_removes_session_from_cache(self, _):
        email = 'someone@somedomain.tld'
        self.provider.address_for.return_value = email
        session = self._create_session()

        key = SessionCache.session_key(self.provider, self.auth.username)
        SessionCache.remember_session(key, session)

        self.assertEqual(session, SessionCache.lookup_session(key))

        with patch('pixelated.config.sessions.unregister') as unregister_mock:
            session.close()

        self.assertIsNone(SessionCache.lookup_session(key))

    @patch('pixelated.config.sessions.register')
    def test_close_ends_account_session(self, _):
        account_mock = MagicMock()
        email = 'someone@somedomain.tld'
        self.provider.address_for.return_value = email
        session = self._create_session()
        session.account = account_mock

        with patch('pixelated.config.sessions.unregister') as unregister_mock:
            session.close()

        account_mock.end_session.assert_called_once_with()

    @patch('pixelated.config.sessions.register')
    def test_session_fresh_is_initially_false(self, _):
        session = self._create_session()

        self.assertFalse(session.fresh_account)

    @patch('pixelated.config.sessions.register')
    def test_session_sets_status_to_fresh_on_key_generation_event(self, _):
        session = self._create_session()
        self.provider.address_for.return_value = 'someone@somedomain.tld'

        session._set_fresh_account(None, 'someone@somedomain.tld')

        self.assertTrue(session.fresh_account)

    @patch('pixelated.config.sessions.register')
    def test_closed_session_not_reused(self, _):
        session = self._create_session()
        SessionCache.remember_session('somekey', session)
        session._is_closed = True

        result = SessionCache.lookup_session('somekey')

        self.assertIsNone(result)

    @patch('pixelated.config.sessions.register')
    def test_session_does_not_set_status_fresh_for_unkown_emails(self, _):
        session = self._create_session()
        self.provider.address_for.return_value = 'someone@somedomain.tld'

        session._set_fresh_account(None, 'another_email@somedomain.tld')

        self.assertFalse(session.fresh_account)

    def test_session_setup_soledad_with_utf8_characters(self):
        api_cert = MagicMock()
        leap_session_factory = LeapSessionFactory(self.provider)

        with patch('pixelated.config.sessions.threads.deferToThread') as deferToThreadMock:
            leap_session_factory.setup_soledad('self.token', u'self.uuid', 'Klünter', api_cert)
            deferToThreadMock.assert_called_once()
            args, kwargs = deferToThreadMock.call_args
            uuid_arg = args[1]
            pass_arg = kwargs['passphrase']
            self.assertIs(type(uuid_arg), str, "expected uuid argument to be a string")
            self.assertIs(type(pass_arg), unicode, "expected passphrase argument to be unicode")

    @defer.inlineCallbacks
    def test_sessions__setup_soledad__will_raise_wrong_passphrase_exception_on_errors(self):
        leap_session_factory = LeapSessionFactory(self.provider)

        with patch('pixelated.config.sessions.Soledad', side_effect=WrongMacError("oh no")):
            with self.assertRaises(SoledadWrongPassphraseException):
                yield leap_session_factory.setup_soledad('token', u'uuid', 'passphrase', None)

        with patch('pixelated.config.sessions.Soledad', side_effect=UnknownMacMethodError("oh no")):
            with self.assertRaises(SoledadWrongPassphraseException):
                yield leap_session_factory.setup_soledad('token', u'uuid', 'passphrase', None)

    def _create_session(self):
        return LeapSession(self.provider, self.auth, self.mail_store, self.soledad_session, self.keymanager, self.smtp_mock)


def _execute_func(func):
    func()
