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

import os

from twisted.internet import defer, reactor
from twisted.logger import Logger

from pixelated.adapter.mailstore.leap_attachment_store import LeapAttachmentStore
from pixelated.adapter.mailstore.searchable_mailstore import SearchableMailStore
from pixelated.adapter.services.mail_service import MailService
from pixelated.adapter.model.mail import InputMail
from pixelated.adapter.services.mail_sender import MailSender
from pixelated.adapter.search import SearchEngine
from pixelated.adapter.services.draft_service import DraftService
from pixelated.adapter.listeners.mailbox_indexer_listener import listen_all_mailboxes
from pixelated.adapter.search.index_storage_key import SearchIndexStorageKey
from pixelated.adapter.services.feedback_service import FeedbackService
from pixelated.config import leap_config

logger = Logger()


class Services(object):

    def __init__(self, leap_session):
        self._leap_home = leap_config.leap_home
        self._pixelated_home = os.path.join(self._leap_home, 'pixelated')
        self._leap_session = leap_session

    @defer.inlineCallbacks
    def setup(self):
        search_index_storage_key = self._setup_search_index_storage_key(self._leap_session.soledad)
        yield self._setup_search_engine(self._leap_session.user_auth.uuid, search_index_storage_key)

        self._wrap_mail_store_with_indexing_mail_store(self._leap_session)

        yield listen_all_mailboxes(self._leap_session.account, self.search_engine, self._leap_session.mail_store)

        self.mail_service = self._setup_mail_service(self.search_engine)

        self.keymanager = self._leap_session.keymanager
        self.draft_service = self._setup_draft_service(self._leap_session.mail_store)
        self.feedback_service = self._setup_feedback_service()
        yield self._index_all_mails()

    def close(self):
        self._leap_session.close()

    def _wrap_mail_store_with_indexing_mail_store(self, leap_session):
        leap_session.mail_store = SearchableMailStore(leap_session.mail_store, self.search_engine)

    @defer.inlineCallbacks
    def _index_all_mails(self):
        all_mails = yield self.mail_service.all_mails()
        self.search_engine.index_mails(all_mails)

    @defer.inlineCallbacks
    def _setup_search_engine(self, namespace, search_index_storage_key):
        key_unicode = yield search_index_storage_key.get_or_create_key()
        key = str(key_unicode)
        logger.debug('The key len is: %s' % len(key))
        user_id = self._leap_session.user_auth.uuid
        user_folder = os.path.join(self._pixelated_home, user_id)
        search_engine = SearchEngine(key, user_home=user_folder)
        self.search_engine = search_engine

    def _setup_mail_service(self, search_engine):
        pixelated_mail_sender = MailSender(self._leap_session.smtp_config, self._leap_session.keymanager.keymanager)

        return MailService(
            pixelated_mail_sender,
            self._leap_session.mail_store,
            search_engine,
            self._leap_session.account_email(),
            LeapAttachmentStore(self._leap_session.soledad))

    def _setup_draft_service(self, mail_store):
        return DraftService(mail_store)

    def _setup_search_index_storage_key(self, soledad):
        return SearchIndexStorageKey(soledad)

    def _setup_feedback_service(self):
        return FeedbackService(self._leap_session)


class ServicesFactory(object):

    def __init__(self, mode):
        self._services_by_user = {}
        self.mode = mode
        self._map_email = {}

    def map_email(self, username, user_id):
        self._map_email[username] = user_id

    def has_session(self, user_id):
        return user_id in self._services_by_user

    def services(self, user_id):
        return self._services_by_user[user_id]

    def destroy_session(self, user_id, using_email=False):
        if using_email:
            username = user_id.split('@')[0]
            user_id = self._map_email.get(username, None)

        if user_id is not None and self.has_session(user_id):
            _services = self._services_by_user[user_id]
            _services.close()
            del self._services_by_user[user_id]

    def add_session(self, user_id, services):
        self._services_by_user[user_id] = services

    def online_sessions(self):
        return len(self._services_by_user.keys())

    @defer.inlineCallbacks
    def create_services_from(self, leap_session):
        _services = Services(leap_session)
        yield _services.setup()
        self._services_by_user[leap_session.user_auth.uuid] = _services


class SingleUserServicesFactory(object):
    def __init__(self, mode):
        self._services = None
        self.mode = mode

    def add_session(self, user_id, services):
        self._services = services

    def services(self, user_id):
        return self._services

    def has_session(self, user_id):
        return True

    def destroy_session(self, user_id, using_email=False):
        reactor.stop()

    def online_sessions(self):
        return 1
