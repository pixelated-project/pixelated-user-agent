from pixelated.adapter.mailstore.searchable_mailstore import SearchableMailStore
from pixelated.adapter.services.mail_service import MailService
from pixelated.adapter.model.mail import InputMail
from pixelated.adapter.services.mail_sender import MailSender
from pixelated.adapter.search import SearchEngine
from pixelated.adapter.services.draft_service import DraftService
from pixelated.adapter.listeners.mailbox_indexer_listener import listen_all_mailboxes
from twisted.internet import defer
from pixelated.adapter.search.index_storage_key import SearchIndexStorageKey
from pixelated.adapter.services.feedback_service import FeedbackService


class Services(object):

    def __init__(self, leap_home, leap_session):
        pass

    @defer.inlineCallbacks
    def setup(self, leap_home, leap_session):
        InputMail.FROM_EMAIL_ADDRESS = leap_session.account_email()

        search_index_storage_key = self.setup_search_index_storage_key(leap_session.soledad_session.soledad)
        yield self.setup_search_engine(
            leap_home,
            search_index_storage_key)

        self.wrap_mail_store_with_indexing_mail_store(leap_session)

        yield listen_all_mailboxes(leap_session.account, self.search_engine, leap_session.mail_store)

        self.mail_service = self.setup_mail_service(
            leap_session,
            self.search_engine)

        self.keymanager = leap_session.nicknym
        self.draft_service = self.setup_draft_service(leap_session.mail_store)
        self.feedback_service = self.setup_feedback_service(leap_session)

        yield self.index_all_mails()

    def wrap_mail_store_with_indexing_mail_store(self, leap_session):
        leap_session.mail_store = SearchableMailStore(leap_session.mail_store, self.search_engine)

    @defer.inlineCallbacks
    def index_all_mails(self):
        all_mails = yield self.mail_service.all_mails()
        self.search_engine.index_mails(all_mails)

    @defer.inlineCallbacks
    def setup_search_engine(self, leap_home, search_index_storage_key):
        key_unicode = yield search_index_storage_key.get_or_create_key()
        key = str(key_unicode)
        print 'The key len is: %s' % len(key)
        search_engine = SearchEngine(key, agent_home=leap_home)
        self.search_engine = search_engine

    def setup_mail_service(self, leap_session, search_engine):
        # if False:   FIXME
        #    yield pixelated_mailboxes.add_welcome_mail_for_fresh_user()
        pixelated_mail_sender = MailSender(
            leap_session.account_email(),
            leap_session.smtp)
        return MailService(
            pixelated_mail_sender,
            leap_session.mail_store,
            search_engine)

    def setup_draft_service(self, mail_store):
        return DraftService(mail_store)

    def setup_search_index_storage_key(self, soledad):
        return SearchIndexStorageKey(soledad)

    def setup_feedback_service(self, leap_session):
        return FeedbackService(leap_session)
