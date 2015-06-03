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
from mockito import mock
import os
import shutil
import time
import uuid

from leap.mail.imap.account import IMAPAccount
from leap.soledad.client import Soledad
from mock import MagicMock, Mock
from twisted.internet import reactor
from twisted.internet.defer import succeed
from twisted.web.resource import getChildForRequest
from twisted.web.server import Site

from pixelated.adapter.model.mail import PixelatedMail
from pixelated.adapter.search import SearchEngine
from pixelated.adapter.services.draft_service import DraftService
from pixelated.adapter.services.mail_service import MailService
from pixelated.adapter.services.mailboxes import Mailboxes
from pixelated.adapter.soledad.soledad_querier import SoledadQuerier
from pixelated.config import App
from pixelated.resources.root_resource import RootResource
from test.support.integration.model import MailBuilder
from test.support.test_helper import request_mock
from test.support.integration.model import ResponseMail


class AppTestClient(object):
    INDEX_KEY = '\xde3?\x87\xff\xd9\xd3\x14\xf0\xa7>\x1f%C{\x16.\\\xae\x8c\x13\xa7\xfb\x04\xd4]+\x8d_\xed\xd1\x8d\x0bI' \
                '\x8a\x0e\xa4tm\xab\xbf\xb4\xa5\x99\x00d\xd5w\x9f\x18\xbc\x1d\xd4_W\xd2\xb6\xe8H\x83\x1b\xd8\x9d\xad'
    ACCOUNT = 'test'
    MAIL_ADDRESS = 'test@pixelated.org'

    def __init__(self):
        self.start_client()

    def start_client(self):
        soledad_test_folder = self._generate_soledad_test_folder_name()
        SearchEngine.DEFAULT_INDEX_HOME = soledad_test_folder

        self.cleanup = lambda: shutil.rmtree(soledad_test_folder)

        PixelatedMail.from_email_address = self.MAIL_ADDRESS

        self.soledad = initialize_soledad(tempdir=soledad_test_folder)
        self.soledad_querier = self._create_soledad_querier(self.soledad, self.INDEX_KEY)
        self.keymanager = mock()

        self.search_engine = SearchEngine(self.soledad_querier, agent_home=soledad_test_folder)
        self.mail_sender = self._create_mail_sender()

        self.account = IMAPAccount(self.ACCOUNT, self.soledad, MagicMock())
        self.mailboxes = Mailboxes(self.account, self.soledad_querier, self.search_engine)
        self.draft_service = DraftService(self.mailboxes)

        self.mail_service = self._create_mail_service(self.mailboxes, self.mail_sender, self.soledad_querier, self.search_engine)
        self.search_engine.index_mails(self.mail_service.all_mails())

        self.app = App()
        self.app.resource = RootResource()
        self.app.resource.initialize(self.soledad_querier, self.keymanager, self.search_engine, self.mail_service, self.draft_service)

    def _render(self, request, as_json=True):
        def get_str(_str):
            return json.loads(_str) if as_json else _str

        def get_request_written_data(_=None):
            written_data = request.getWrittenData()
            if written_data:
                return get_str(written_data)

        resource = getChildForRequest(self.app.resource, request)
        result = resource.render(request)

        if isinstance(result, basestring):
            return get_str(result), request

        # result is NOT_DONE_YET
        d = succeed(request) if request.finished else request.notifyFinish()
        d.addCallback(get_request_written_data)
        return d, request

    def run_on_a_thread(self, logfile='/tmp/app_test_client.log', port=4567, host='0.0.0.0'):
        def _start():
            reactor.listenTCP(port, Site(self.app.resource), interface=host)
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

    def add_document_to_soledad(self, _dict):
        self.soledad_querier.soledad.create_doc(_dict)

    def add_mail_to_inbox(self, input_mail):
        mail = self.mailboxes.inbox().add(input_mail)
        if input_mail.tags:
            mail.update_tags(input_mail.tags)
            self.search_engine.index_mail(mail)

    def add_multiple_to_mailbox(self, num, mailbox='', flags=[], tags=[], to='recipient@to.com', cc='recipient@cc.com', bcc='recipient@bcc.com'):
        mails = []
        for _ in range(num):
            input_mail = MailBuilder().with_status(flags).with_tags(tags).with_to(to).with_cc(cc).with_bcc(bcc).build_input_mail()
            mail = self.mailboxes._create_or_get(mailbox).add(input_mail)
            mails.append(mail)
            mail.update_tags(input_mail.tags) if tags else None
        self.search_engine.index_mails(mails) if tags else None
        return mails

    def _create_soledad_querier(self, soledad, index_key):
        soledad_querier = SoledadQuerier(soledad)
        soledad_querier.get_index_masterkey = lambda: index_key
        return soledad_querier

    def _create_mail_sender(self):
        mail_sender = Mock()
        mail_sender.sendmail.side_effect = lambda mail: succeed(mail)
        return mail_sender

    def _create_mail_service(self, mailboxes, mail_sender, soledad_querier, search_engine):
        mail_service = MailService(mailboxes, mail_sender, soledad_querier, search_engine)
        return mail_service

    def _generate_soledad_test_folder_name(self, soledad_test_folder='/tmp/soledad-test/test'):
        return os.path.join(soledad_test_folder, str(uuid.uuid4()))

    def get_mails_by_tag(self, tag, page=1, window=100):
        tags = 'tag:%s' % tag
        return self.search(tags, page, window)

    def search(self, query, page=1, window=100):
        res, req = self.get("/mails", {
            'q': [query],
            'w': [str(window)],
            'p': [str(page)]
        })
        return [ResponseMail(m) for m in res['mails']]

    def get_attachment(self, ident, encoding):
        res, req = self.get("/attachment/%s" % ident, {'encoding': [encoding]}, as_json=False)
        return res

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
        return req

    def delete_mails(self, idents):
        res, req = self.post("/mails/delete", json.dumps({'idents': idents}))
        return req

    def mark_many_as_unread(self, idents):
        res, req = self.post('/mails/unread', json.dumps({'idents': idents}))
        return req

    def mark_many_as_read(self, idents):
        res, req = self.post('/mails/read', json.dumps({'idents': idents}))
        return req

    def get_contacts(self, query):
        res, req = self.get('/contacts', get_args={'q': query})
        return res


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
    return _soledad
