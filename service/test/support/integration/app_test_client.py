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
import json
import multiprocessing
import os
import shutil
import time
import uuid
import random

from pixelated.authentication import Authentication
from tempdir import TempDir

from mock import Mock
from mockito import mock

from twisted.cred import checkers, credentials
from twisted.internet import reactor, defer
from twisted.internet.defer import succeed
from twisted.web.resource import getChildForRequest
from zope.interface import implementer

from leap.bitmask.mail.mail import Account
from leap.soledad.client import Soledad
from leap.bitmask.mail.adaptors.soledad import SoledadMailAdaptor
from pixelated.adapter.mailstore.leap_attachment_store import LeapAttachmentStore
from pixelated.adapter.services.feedback_service import FeedbackService
from pixelated.application import UserAgentMode, set_up_protected_resources
from pixelated.config.sessions import LeapSession
from pixelated.config.services import Services, ServicesFactory, SingleUserServicesFactory
from pixelated.config.site import PixelatedSite

from pixelated.adapter.mailstore import LeapMailStore
from pixelated.adapter.mailstore.searchable_mailstore import SearchableMailStore
from pixelated.adapter.search import SearchEngine
from pixelated.adapter.services.draft_service import DraftService
from pixelated.adapter.services.mail_service import MailService
from pixelated.resources.root_resource import RootResource
from test.support.integration.model import MailBuilder
from test.support.test_helper import request_mock
from test.support.integration.model import ResponseMail
from pixelated.config.sessions import SessionCache


class AppTestAccount(object):
    INDEX_KEY = '\xde3?\x87\xff\xd9\xd3\x14\xf0\xa7>\x1f%C{\x16.\\\xae\x8c\x13\xa7\xfb\x04\xd4]+\x8d_\xed\xd1\x8d\x0bI' \
                '\x8a\x0e\xa4tm\xab\xbf\xb4\xa5\x99\x00d\xd5w\x9f\x18\xbc\x1d\xd4_W\xd2\xb6\xe8H\x83\x1b\xd8\x9d\xad'

    def __init__(self, user_id, leap_home):
        self._user_id = user_id
        self._leap_home = leap_home
        self._pixelated_home = os.path.join(self._leap_home, 'pixelated')
        self._uuid = str(uuid.uuid4())
        self._mail_address = '%s@pixelated.org' % user_id
        self._soledad = None
        self._services = None
        self.soledad_test_folder = os.path.join(self._pixelated_home, self._uuid)

    @defer.inlineCallbacks
    def start(self):
        self.soledad = yield initialize_soledad(tempdir=self.soledad_test_folder, uuid=self._uuid)
        self.search_engine = SearchEngine(self.INDEX_KEY, user_home=self.soledad_test_folder)
        self.keymanager = mock()
        self.mail_sender = self._create_mail_sender()
        self.mail_store = SearchableMailStore(LeapMailStore(self.soledad), self.search_engine)
        self.attachment_store = LeapAttachmentStore(self.soledad)

        yield self._initialize_account()

        self.draft_service = DraftService(self.mail_store)
        self.leap_session = mock()
        self.feedback_service = FeedbackService(self.leap_session)

        self.mail_service = self._create_mail_service(self.mail_sender, self.mail_store, self.search_engine, self.attachment_store)

        mails = yield self.mail_service.all_mails()
        if len(mails) > 0:
            raise Exception('What? Where did these come from?')
        self.search_engine.index_mails(mails)

    @property
    def services(self):
        if self._services is None:
            services = mock(Services)
            services.keymanager = self.keymanager
            services.mail_service = self.mail_service
            services.draft_service = self.draft_service
            services.search_engine = self.search_engine
            services.feedback_service = self.feedback_service
            services._leap_session = self.leap_session

            self._services = services
            self.leap_session.close = lambda: 'mocked'

        return self._services

    def cleanup(self):
        shutil.rmtree(self.soledad_test_folder)

    def _initialize_account(self):
        self.account = Account(self.soledad, self._user_id)
        return self.account.deferred_initialization

    def _create_mail_service(self, mail_sender, mail_store, search_engine, attachment_store):
        return MailService(mail_sender, mail_store, search_engine, self._mail_address, attachment_store)

    def _create_mail_sender(self):
        mail_sender = Mock()
        mail_sender.sendmail.side_effect = lambda mail: succeed(mail)
        return mail_sender


@implementer(checkers.ICredentialsChecker)
class StubSRPChecker(object):
    credentialInterfaces = (
        credentials.IUsernamePassword,
    )

    def __init__(self, leap_provider, credentials={}):
        self._leap_provider = leap_provider
        self._credentials = credentials.copy()

    def add_user(self, username, password):
        self._credentials[username] = password

    def requestAvatarId(self, credentials):
        if(self._credentials[credentials.username] == credentials.password):
            leap_auth = Authentication(credentials.username, uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), {})
            return defer.succeed(LeapSession(self._leap_provider, leap_auth, None, None, None, None))
        else:
            return defer.fail()


class StubAuthenticator(object):
    def __init__(self, provider, credentials={}):
        self._leap_provider = provider
        self._credentials = credentials.copy()

    def add_user(self, username, password):
        self._credentials[username] = password

    def _set_leap_session_cache(self, auth):
        key = SessionCache.session_key(self._leap_provider, 'username')
        SessionCache.remember_session(key, LeapSession(self._leap_provider, auth, None, None, None, None))

    def authenticate(self, username, password):
        if self._credentials[username] == password:
            leap_auth = Authentication(username, uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), {})
            self._set_leap_session_cache(leap_auth)
            return defer.succeed(leap_auth)
        else:
            return defer.fail()


class StubServicesFactory(ServicesFactory):

    def __init__(self, accounts, mode):
        super(StubServicesFactory, self).__init__(mode=mode)
        self._accounts = accounts

    @defer.inlineCallbacks
    def create_services_from(self, leap_session):
        account = self._accounts[leap_session.user_auth.username]
        self._services_by_user[leap_session.user_auth.uuid] = account.services
        yield defer.succeed(None)


# TODO: some methods are used by 1 test class only, maybe push them down there
class AppTestClient(object):
    INDEX_KEY = '\xde3?\x87\xff\xd9\xd3\x14\xf0\xa7>\x1f%C{\x16.\\\xae\x8c\x13\xa7\xfb\x04\xd4]+\x8d_\xed\xd1\x8d\x0bI' \
                '\x8a\x0e\xa4tm\xab\xbf\xb4\xa5\x99\x00d\xd5w\x9f\x18\xbc\x1d\xd4_W\xd2\xb6\xe8H\x83\x1b\xd8\x9d\xad'
    ACCOUNT = 'test'
    MAIL_ADDRESS = 'test@pixelated.org'

    def _initialize(self):
        self._tmp_dir = TempDir()
        self.accounts = {}

    @defer.inlineCallbacks
    def start_client(self, mode=UserAgentMode(is_single_user=True)):
        self._initialize()
        self._mode = mode
        self._test_account = AppTestAccount(self.ACCOUNT, self._tmp_dir.name)

        yield self._test_account.start()

        self.cleanup = lambda: self._tmp_dir.dissolve()

        # copy fields for single user tests
        self.soledad = self._test_account.soledad
        self.search_engine = self._test_account.search_engine
        self.keymanager = self._test_account.keymanager
        self.mail_sender = self._test_account.mail_sender
        self.mail_store = self._test_account.mail_store
        self.attachment_store = self._test_account.attachment_store
        self.draft_service = self._test_account.draft_service
        self.leap_session = self._test_account.leap_session
        self.feedback_service = self._test_account.feedback_service
        self.mail_service = self._test_account.mail_service
        self.account = self._test_account.account

        if mode.is_single_user:
            self.service_factory = SingleUserServicesFactory(mode)
            services = self._test_account.services
            self.service_factory.add_session('someuserid', services)

            self.resource = RootResource(self.service_factory)
            provider = mock()
            self.resource.initialize(provider)
        else:
            self.service_factory = StubServicesFactory(self.accounts, mode)
            provider = mock()
            bonafide_checker = StubAuthenticator(provider)
            bonafide_checker.add_user('username', 'password')

            self.resource = set_up_protected_resources(RootResource(self.service_factory), provider, self.service_factory, authenticator=bonafide_checker)

    @defer.inlineCallbacks
    def create_user(self, account_name):
        if self._mode.is_single_user:
            raise Exception('Not supported in single user mode')

        account = AppTestAccount(account_name, self._tmp_dir.name)
        yield account.start()

        self.accounts[account_name] = account

    def _render(self, request, as_json=True):
        def get_str(_str):
            return json.loads(_str) if as_json else _str

        def get_request_written_data(_=None):
            written_data = request.getWrittenData()
            if written_data:
                return get_str(written_data)

        resource = getChildForRequest(self.resource, request)
        result = resource.render(request)

        if isinstance(result, basestring):
            return get_str(result), request

        # result is NOT_DONE_YET
        d = succeed(request) if request.finished else request.notifyFinish()
        d.addCallback(get_request_written_data)
        return d, request

    def listenTCP(self, port=4567, host='127.0.0.1'):
        reactor.listenTCP(port, PixelatedSite(self.resource), interface=host)

    def run_on_a_thread(self, logfile='/tmp/app_test_client.log', port=4567, host='127.0.0.1'):
        def _start():
            self.listenTCP(port, host)
            reactor.run()
        process = multiprocessing.Process(target=_start)
        process.start()
        time.sleep(1)
        return lambda: process.terminate()

    def stop(self):
        reactor.stop()

    def get(self, path, get_args='', as_json=True, ajax=True, csrf='token'):
        request = request_mock(path, ajax=ajax, csrf=csrf)
        request.args = get_args
        return self._render(request, as_json)

    def post(self, path, body='', headers=None, ajax=True, csrf='token'):
        headers = headers or {'Content-Type': 'application/json'}
        request = request_mock(path=path, method="POST", body=body, headers=headers, ajax=ajax, csrf=csrf)
        return self._render(request)

    def put(self, path, body, ajax=True, csrf='token'):
        request = request_mock(path=path, method="PUT", body=body, headers={'Content-Type': ['application/json']}, ajax=ajax, csrf=csrf)
        return self._render(request)

    def delete(self, path, body="", ajax=True, csrf='token'):
        request = request_mock(path=path, body=body, headers={'Content-Type': ['application/json']}, method="DELETE", ajax=ajax, csrf=csrf)
        return self._render(request)

    @defer.inlineCallbacks
    def add_mail_to_inbox(self, input_mail):
        mail = yield self.mail_store.add_mail('INBOX', input_mail.raw)
        defer.returnValue(mail)

    def account_for(self, username):
        return self.accounts[username]

    # TODO: remove
    def add_mail_to_user_inbox(self, input_mail, username):
        return self.account_for(username).mail_store.add_mail('INBOX', input_mail.raw)

    @defer.inlineCallbacks
    def add_multiple_to_mailbox(self, num, mailbox='', flags=[], tags=[], to='recipient@to.com', cc='recipient@cc.com', bcc='recipient@bcc.com'):
        mails = []
        yield self.mail_store.add_mailbox(mailbox)
        for _ in range(num):
            builder = MailBuilder().with_status(flags).with_tags(tags).with_to(to).with_cc(cc).with_bcc(bcc)
            builder.with_body(str(random.random()))
            input_mail = builder.build_input_mail()
            mail = yield self.mail_store.add_mail(mailbox, input_mail.raw)
            if tags:
                mail.tags |= set(tags)
            if flags:
                for flag in flags:
                    mail.flags.add(flag)
            if tags or flags:
                yield self.mail_store.update_mail(mail)
            mails.append(mail)

        defer.returnValue(mails)

    def _create_mail_sender(self):
        mail_sender = Mock()
        mail_sender.sendmail.side_effect = lambda mail: succeed(mail)
        return mail_sender

    # TODO: remove
    def _generate_soledad_test_folder_name(self, soledad_test_folder='/tmp/soledad-test/test'):
        return os.path.join(soledad_test_folder, str(uuid.uuid4()))

    def get_mails_by_tag(self, tag, page=1, window=100):
        tags = 'tag:%s' % tag
        return self.search(tags, page, window)

    @defer.inlineCallbacks
    def search(self, query, page=1, window=100):
        res, _ = self.get("/mails", {
            'q': [query],
            'w': [str(window)],
            'p': [str(page)]
        })
        res = yield res
        defer.returnValue([ResponseMail(m) for m in res['mails']])

    # TODO: remove
    @defer.inlineCallbacks
    def get_mails_by_mailbox_name(self, mbox_name):
        mail_ids = yield self.mail_store.get_mailbox_mail_ids(mbox_name)
        mails = yield self.mail_store.get_mails(mail_ids)
        defer.returnValue(mails)

    @defer.inlineCallbacks
    def get_attachment(self, ident, encoding, filename=None, content_type=None, ajax=True, csrf='token'):
        params = {'encoding': [encoding]}
        if filename:
            params['filename'] = [filename]
        if content_type:
            params['content_type'] = [content_type]
        deferred_result, req = self.get("/attachment/%s" % ident, params, as_json=False, ajax=ajax, csrf=csrf)
        res = yield deferred_result
        defer.returnValue((res, req))

    @defer.inlineCallbacks
    def post_attachment(self, data, headers):
        deferred_result, req = self.post('/attachment', body=data, headers=headers)
        res = yield deferred_result
        defer.returnValue((res, req))

    def put_mail(self, data):
        res, req = self.put('/mails', data)
        return res, req

    def post_tags(self, mail_ident, tags_json):
        res, req = self.post("/mail/%s/tags" % mail_ident, tags_json)
        return res

    def get_tags(self, **kwargs):
        res, req = self.get('/tags', kwargs)
        return res

    def get_mail(self, mail_ident):
        res, req = self.get('/mail/%s' % mail_ident)
        return res

    # TODO: remove
    def delete_mail(self, mail_ident):
        res, req = self.delete("/mail/%s" % mail_ident)
        return res

    def delete_mails(self, idents):
        res, req = self.post("/mails/delete", json.dumps({'idents': idents}))
        return res

    def mark_many_as_unread(self, idents):
        res, req = self.post('/mails/unread', json.dumps({'idents': idents}))
        return res

    def mark_many_as_read(self, idents):
        res, req = self.post('/mails/read', json.dumps({'idents': idents}))
        return res

    def get_contacts(self, query):
        res, req = self.get('/contacts', get_args={'q': query})
        return res


@defer.inlineCallbacks
def initialize_soledad(tempdir, uuid):
    if os.path.isdir(tempdir):
        shutil.rmtree(tempdir)

    passphrase = u"verysecretpassphrase"
    secret_path = os.path.join(tempdir, "secret.gpg")
    local_db_path = os.path.join(tempdir, "soledad.u1db")
    server_url = "http://provider"
    cert_file = ""

    class MockSharedDB(object):
        get_doc = Mock(return_value=None)
        put_doc = Mock()
        lock = Mock(return_value=('atoken', 300))
        unlock = Mock(return_value=True)
        close = Mock()

        def __call__(self):
            return self

    Soledad._shared_db = MockSharedDB()

    _soledad = Soledad(
        uuid,
        passphrase,
        secret_path,
        local_db_path,
        server_url,
        cert_file,
        defer_encryption=False,
        syncable=False)

    yield SoledadMailAdaptor().initialize_store(_soledad)

    defer.returnValue(_soledad)
