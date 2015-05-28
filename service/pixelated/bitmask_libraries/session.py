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
import errno
import traceback
import sys

import os
from leap.mail.incoming.service import IncomingMail
from pixelated.bitmask_libraries.config import LeapConfig
from pixelated.bitmask_libraries.provider import LeapProvider
from pixelated.bitmask_libraries.certs import refresh_ca_bundle
from pixelated.adapter.listeners.mailbox_indexer_listener import MailboxIndexerListener
from twisted.internet import reactor
from .nicknym import NickNym
from leap.auth import SRPAuth
from leap.mail.mail import Account
from .soledad import SoledadSessionFactory, SoledadSession
from .smtp import LeapSmtp
from .config import DEFAULT_LEAP_HOME


SESSIONS = {}


def open(username, password, server_name, leap_home=DEFAULT_LEAP_HOME):
    config = LeapConfig(leap_home=leap_home)
    provider = LeapProvider(server_name, config)
    refresh_ca_bundle(provider)
    session = LeapSessionFactory(provider).create(username, password)

    return session


class LeapSession(object):
    """
    A LEAP session.


    Properties:

    - ``leap_config`` the configuration for this session (LeapClientConfig).

    - ``srp_session`` the secure remote password session to authenticate with LEAP. See http://en.wikipedia.org/wiki/Secure_Remote_Password_protocol (LeapSecureRemotePassword)

    - ``soledad_session`` the soledad session. See https://leap.se/soledad (LeapSecureRemotePassword)

    - ``nicknym`` the nicknym instance. See https://leap.se/nicknym (NickNym)

    - ``account`` the actual leap mail account. Implements Twisted imap4.IAccount and imap4.INamespacePresenter (SoledadBackedAccount)

    - ``incoming_mail_fetcher`` Background job for fetching incoming mails from LEAP server (LeapIncomingMail)
    """

    def __init__(self, provider, user_auth, soledad_session, nicknym, incoming_mail_fetcher, smtp, account):
        """
        Constructor.

        :param leap_config: The config for this LEAP session
        :type leap_config: LeapConfig

        """
        self.smtp = smtp
        self.account = account
        self.config = provider.config
        self.provider = provider
        self.user_auth = user_auth
        self.soledad_session = soledad_session
        self.nicknym = nicknym
        self.incoming_mail_fetcher = incoming_mail_fetcher

        if self.config.start_background_jobs:
            self.start_background_jobs()

    def account_email(self):
        domain = self.provider.domain
        name = self.user_auth.username
        return '%s@%s' % (name, domain)

    def close(self):
        self.stop_background_jobs()

    def start_background_jobs(self):
        reactor.callFromThread(self.incoming_mail_fetcher.startService)

    def stop_background_jobs(self):
        reactor.callFromThread(self.incoming_mail_fetcher.stopService)

    def sync(self):
        try:
            self.soledad_session.sync()
        except:
            traceback.print_exc(file=sys.stderr)
            raise


class LeapSessionFactory(object):
    def __init__(self, provider):
        self._provider = provider
        self._config = provider.config

    def create(self, username, password):
        key = self._session_key(username)
        session = self._lookup_session(key)
        if not session:
            session = self._create_new_session(username, password)
            self._remember_session(key, session)

        return session

    def _create_new_session(self, username, password):
        self._create_dir(self._provider.config.leap_home)
        self._provider.download_certificate()

        srp_auth = SRPAuth(self._provider.api_uri, self._provider.local_ca_crt)
        auth = srp_auth.authenticate(username, password)

        soledad = SoledadSessionFactory.create(self._provider, auth.token, auth.uuid, password)

        account = Account(soledad.soledad)

        nicknym = self._create_nicknym(auth.username, auth.token, auth.uuid, soledad)
        incoming_mail_fetcher = self._create_incoming_mail_fetcher(nicknym, soledad, auth, auth.username)

        MailboxIndexerListener.MAIL_FETCHER = incoming_mail_fetcher

        smtp = LeapSmtp(self._provider, auth.username, auth.session_id, nicknym.keymanager)

        smtp.ensure_running()

        return LeapSession(self._provider, auth, soledad, nicknym, incoming_mail_fetcher, smtp, account)

    def _lookup_session(self, key):
        global SESSIONS
        if key in SESSIONS:
            return SESSIONS[key]
        else:
            return None

    def _remember_session(self, key, session):
        global SESSIONS
        SESSIONS[key] = session

    def _session_key(self, username):
        return hash((self._provider, username))

    def _create_dir(self, path):
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def _create_nicknym(self, username, token, uuid, soledad_session):
        return NickNym(self._provider, self._config, soledad_session, username, token, uuid)

    def _create_incoming_mail_fetcher(self, nicknym, soledad_session, auth, username):
        return IncomingMail(nicknym.keymanager,
                            soledad_session.soledad,
                            auth.uuid,
                            self._config.fetch_interval_in_s)

    def _account_email(self, username):
        domain = self._provider.domain
        return '%s@%s' % (username, domain)
