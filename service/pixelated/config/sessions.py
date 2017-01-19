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

from __future__ import absolute_import

import os
import errno
import traceback
import requests
import sys

from twisted.internet import defer, threads, reactor
from twisted.logger import Logger

from leap.soledad.common.crypto import WrongMacError, UnknownMacMethodError
from leap.soledad.client import Soledad
from leap.bitmask.mail.incoming.service import IncomingMail
from leap.bitmask.mail.mail import Account
import leap.common.certs as leap_certs
from leap.common.events import (
    register, unregister,
    catalog as events
)

from pixelated.bitmask_libraries.keymanager import Keymanager, UploadKeyError
from pixelated.adapter.mailstore import LeapMailStore
from pixelated.config import leap_config
from pixelated.bitmask_libraries.certs import LeapCertificate
from pixelated.bitmask_libraries.smtp import LeapSMTPConfig

logger = Logger()


class LeapSessionFactory(object):
    def __init__(self, provider):
        self._provider = provider

    @defer.inlineCallbacks
    def create(self, username, password, auth):
        key = SessionCache.session_key(self._provider, username)
        session = SessionCache.lookup_session(key)
        if not session:
            session = yield self._create_new_session(username, password, auth)
            yield session.first_required_sync()
            SessionCache.remember_session(key, session)
        defer.returnValue(session)

    @defer.inlineCallbacks
    def _create_new_session(self, username, password, auth):
        account_email = self._provider.address_for(username)

        self._create_database_dir(auth.uuid)

        api_cert = self._provider.provider_api_cert

        soledad = yield self.setup_soledad(auth.token, auth.uuid, password, api_cert)

        mail_store = LeapMailStore(soledad)

        keymanager = yield self.setup_keymanager(self._provider, soledad, account_email, auth.token, auth.uuid)

        smtp_client_cert = self._download_smtp_cert(auth)
        smtp_host, smtp_port = self._provider.smtp_info()
        smtp_config = LeapSMTPConfig(account_email, smtp_client_cert, smtp_host, smtp_port)

        leap_session = LeapSession(self._provider, auth, mail_store, soledad, keymanager, smtp_config)

        defer.returnValue(leap_session)

    @defer.inlineCallbacks
    def setup_soledad(self,
                      user_token,
                      user_uuid,
                      password,
                      api_cert):
        secrets = self._secrets_path(user_uuid)
        local_db = self._local_db_path(user_uuid)
        server_url = self._provider.discover_soledad_server(user_uuid)
        try:
            soledad = yield threads.deferToThread(Soledad,
                                                  user_uuid.encode('utf-8'),
                                                  passphrase=unicode(password, 'utf-8'),
                                                  secrets_path=secrets,
                                                  local_db_path=local_db,
                                                  server_url=server_url,
                                                  cert_file=api_cert,
                                                  shared_db=None,
                                                  auth_token=user_token,
                                                  defer_encryption=False)
            defer.returnValue(soledad)
        except (WrongMacError, UnknownMacMethodError), e:
            raise SoledadWrongPassphraseException(e)

    @defer.inlineCallbacks
    def setup_keymanager(self, provider, soledad, account_email, token, uuid):
        keymanager = yield threads.deferToThread(Keymanager,
                                                 provider,
                                                 soledad,
                                                 account_email,
                                                 token,
                                                 uuid)
        defer.returnValue(keymanager)

    def _download_smtp_cert(self, auth):
        cert = SmtpClientCertificate(self._provider, auth, self._user_path(auth.uuid))
        return cert.cert_path()

    def _user_path(self, user_uuid):
        return os.path.join(leap_config.leap_home, user_uuid)

    def _soledad_path(self, user_uuid):
        return os.path.join(leap_config.leap_home, user_uuid, 'soledad')

    def _secrets_path(self, user_uuid):
        return os.path.join(self._soledad_path(user_uuid), 'secrets')

    def _local_db_path(self, user_uuid):
        return os.path.join(self._soledad_path(user_uuid), 'soledad.db')

    def _create_database_dir(self, user_uuid):
        try:
            os.makedirs(self._soledad_path(user_uuid))
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(self._soledad_path(user_uuid)):
                pass
            else:
                raise


class LeapSession(object):

    def __init__(self, provider, user_auth, mail_store, soledad, keymanager, smtp_config):
        self.smtp_config = smtp_config
        self.provider = provider
        self.user_auth = user_auth
        self.mail_store = mail_store
        self.soledad = soledad
        self.keymanager = keymanager
        self.fresh_account = False
        self.incoming_mail_fetcher = None
        self.account = None
        self._has_been_initially_synced = False
        self._is_closed = False
        register(events.KEYMANAGER_FINISHED_KEY_GENERATION, self._set_fresh_account, uid=self.account_email())

    @defer.inlineCallbacks
    def first_required_sync(self):
        yield self.sync()
        yield self.finish_bootstrap()

    @defer.inlineCallbacks
    def finish_bootstrap(self):
        yield self.keymanager.generate_openpgp_key()
        yield self._create_account(self.soledad, self.user_auth.uuid)
        self.incoming_mail_fetcher = yield self._create_incoming_mail_fetcher(
            self.keymanager,
            self.soledad,
            self.account,
            self.account_email())
        reactor.callFromThread(self.incoming_mail_fetcher.startService)

    def _create_account(self, soledad, user_id):
        self.account = Account(soledad, user_id)
        return self.account.deferred_initialization

    def _set_fresh_account(self, event, email_address):
        logger.debug('Key for email %s has been generated' % email_address)
        if email_address == self.account_email():
            self.fresh_account = True

    def account_email(self):
        name = self.user_auth.username
        return self.provider.address_for(name)

    def close(self):
        self.stop_background_jobs()
        unregister(events.KEYMANAGER_FINISHED_KEY_GENERATION, uid=self.account_email())
        self.soledad.close()
        self._close_account()
        self.remove_from_cache()
        self._is_closed = True

    @property
    def is_closed(self):
        return self._is_closed

    def _close_account(self):
        if self.account:
            self.account.end_session()

    def remove_from_cache(self):
        key = SessionCache.session_key(self.provider, self.user_auth.username)
        SessionCache.remove_session(key)

    @defer.inlineCallbacks
    def _create_incoming_mail_fetcher(self, keymanager, soledad, account, user_mail):
        inbox = yield account.callWhenReady(lambda _: account.get_collection_by_mailbox('INBOX'))
        defer.returnValue(IncomingMail(keymanager.keymanager,
                          soledad,
                          inbox,
                          user_mail))

    def stop_background_jobs(self):
        if self.incoming_mail_fetcher:
            reactor.callFromThread(self.incoming_mail_fetcher.stopService)
            self.incoming_mail_fetcher = None

    def sync(self):
        try:
            return self.soledad.sync()
        except Exception as e:
            logger.error(e)
            raise


class SessionCache(object):

    sessions = {}

    @staticmethod
    def lookup_session(key):
        session = SessionCache.sessions.get(key, None)
        if session is not None and session.is_closed:
            SessionCache.remove_session(key)
            return None
        return session

    @staticmethod
    def remember_session(key, session):
        SessionCache.sessions[key] = session

    @staticmethod
    def remove_session(key):
        if key in SessionCache.sessions:
            del SessionCache.sessions[key]

    @staticmethod
    def session_key(provider, username):
        return hash((provider, username))


class SmtpClientCertificate(object):
    def __init__(self, provider, auth, user_path):
        self._provider = provider
        self._auth = auth
        self._user_path = user_path

    def cert_path(self):
        if not self._is_cert_already_downloaded() or self._should_redownload():
            self._download_smtp_cert()

        return self._smtp_client_cert_path()

    def _is_cert_already_downloaded(self):
        return os.path.exists(self._smtp_client_cert_path())

    def _should_redownload(self):
        return leap_certs.should_redownload(self._smtp_client_cert_path())

    def _download_smtp_cert(self):
        cert_path = self._smtp_client_cert_path()

        if not os.path.exists(os.path.dirname(cert_path)):
            os.makedirs(os.path.dirname(cert_path))

        self.download_to(cert_path)

    def _smtp_client_cert_path(self):
        return os.path.join(
            self._user_path,
            "providers",
            self._provider.domain,
            "keys", "client", "smtp.pem")

    def download(self):
        cert_url = '%s/%s/smtp_cert' % (self._provider.api_uri, self._provider.api_version)
        headers = {}
        headers["Authorization"] = 'Token token="{0}"'.format(self._auth.token)
        params = {'address': self._auth.username}
        response = requests.post(
            cert_url,
            params=params,
            data=params,
            verify=self._provider.provider_api_cert,
            timeout=15,
            headers=headers)
        response.raise_for_status()

        client_cert = response.content

        return client_cert

    def download_to(self, target_file):
        client_cert = self.download()

        with open(target_file, 'w') as f:
            f.write(client_cert)


class SoledadWrongPassphraseException(Exception):
    def __init__(self, *args, **kwargs):
        super(SoledadWrongPassphraseException, self).__init__(*args, **kwargs)
