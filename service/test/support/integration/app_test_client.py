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
from leap.mail.adaptors.soledad import SoledadMailAdaptor
from mockito import mock
import os
import shutil
import time
import uuid
import random


from leap.mail.imap.account import IMAPAccount
from leap.soledad.client import Soledad
from mock import Mock
from twisted.internet import reactor, defer
from twisted.internet.defer import succeed
from twisted.web.resource import getChildForRequest
# from twisted.web.server import Site as PixelatedSite
from pixelated.adapter.services.feedback_service import FeedbackService
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


class AppTestClient(object):
    INDEX_KEY = '\xde3?\x87\xff\xd9\xd3\x14\xf0\xa7>\x1f%C{\x16.\\\xae\x8c\x13\xa7\xfb\x04\xd4]+\x8d_\xed\xd1\x8d\x0bI' \
                '\x8a\x0e\xa4tm\xab\xbf\xb4\xa5\x99\x00d\xd5w\x9f\x18\xbc\x1d\xd4_W\xd2\xb6\xe8H\x83\x1b\xd8\x9d\xad'
    ACCOUNT = 'test'
    MAIL_ADDRESS = 'test@pixelated.org'

    # def __init__(self):
    #     self.start_client()

    @defer.inlineCallbacks
    def start_client(self):
        soledad_test_folder = self._generate_soledad_test_folder_name()
        SearchEngine.DEFAULT_INDEX_HOME = soledad_test_folder

        self.cleanup = lambda: shutil.rmtree(soledad_test_folder)

        self.soledad = yield initialize_soledad(tempdir=soledad_test_folder)

        self.keymanager = mock()

        self.search_engine = SearchEngine(self.INDEX_KEY, agent_home=soledad_test_folder)
        self.mail_sender = self._create_mail_sender()

        self.mail_store = SearchableMailStore(LeapMailStore(self.soledad), self.search_engine)

        account_ready_cb = defer.Deferred()
        self.account = IMAPAccount(self.ACCOUNT, self.soledad, account_ready_cb)
        yield account_ready_cb
        self.draft_service = DraftService(self.mail_store)
        self.leap_session = mock()
        self.feedback_service = FeedbackService(self.leap_session)

        self.mail_service = self._create_mail_service(self.mail_sender, self.mail_store, self.search_engine)
        mails = yield self.mail_service.all_mails()
        self.search_engine.index_mails(mails)

        self.resource = RootResource()
        self.resource.initialize(
            self.keymanager, self.search_engine, self.mail_service, self.draft_service, self.feedback_service)

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

    def get(self, path, get_args='', as_json=True):
        request = request_mock(path)
        request.args = get_args
        return self._render(request, as_json)

    def post(self, path, body=''):
        request = request_mock(path=path, method="POST", body=body, headers={'Content-Type': ['application/json']})
        return self._render(request)

    def put(self, path, body):
        request = request_mock(path=path, method="PUT", body=body, headers={'Content-Type': ['application/json']})
        return self._render(request)

    def delete(self, path, body=""):
        request = request_mock(path=path, body=body, headers={'Content-Type': ['application/json']}, method="DELETE")
        return self._render(request)

    @defer.inlineCallbacks
    def add_mail_to_inbox(self, input_mail):
        mail = yield self.mail_store.add_mail('INBOX', input_mail.raw)
        defer.returnValue(mail)

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

    def _create_mail_service(self, mail_sender, mail_store, search_engine):
        mail_service = MailService(mail_sender, mail_store, search_engine)
        return mail_service

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

    @defer.inlineCallbacks
    def get_attachment(self, ident, encoding):
        deferred_result, req = self.get("/attachment/%s" % ident, {'encoding': [encoding]}, as_json=False)
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
def initialize_soledad(tempdir):
    if os.path.isdir(tempdir):
        shutil.rmtree(tempdir)

    uuid = "foobar-uuid"
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
