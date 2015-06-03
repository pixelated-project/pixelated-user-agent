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
import unittest
import email

from pixelated.maintenance import delete_all_mails, load_mails
from pixelated.bitmask_libraries.session import LeapSession
from leap.mail.imap.account import IMAPAccount
from leap.mail.imap.fields import WithMsgFields
from leap.soledad.client import Soledad
from leap.soledad.common.document import SoledadDocument
from mock import MagicMock, ANY
from os.path import join, dirname
from twisted.internet import defer, reactor


class TestCommands(unittest.TestCase):

    def setUp(self):
        self.leap_session = MagicMock(spec=LeapSession)
        self.soledad = MagicMock(spec=Soledad)
        self.account = MagicMock(spec=IMAPAccount)
        self.mailbox = MagicMock()
        self.leap_session.account = self.account
        self.account.getMailbox.return_value = self.mailbox

        self.args = (self.leap_session, self.soledad)

    def test_delete_all_mails_supports_empty_doclist(self):
        self.soledad.get_all_docs.return_value = (1, [])

        delete_all_mails(self.args)

        self.assertFalse(self.soledad.delete_doc.called)

    def test_delete_all_mails(self):
        doc = MagicMock(spec=SoledadDocument)
        doc.content = {'type': 'head'}
        self.soledad.get_all_docs.return_value = (1, [doc])

        delete_all_mails(self.args)

        self.soledad.delete_doc.assert_called_once_with(doc)

    def test_only_mail_documents_are_deleted(self):
        docs = self._create_docs_of_type(['head', 'cnt', 'flags', 'mbx', 'foo', None])
        self.soledad.get_all_docs.return_value = (1, docs)

        delete_all_mails(self.args)

        for doc in docs:
            if doc.content['type'] in ['head', 'cnt', 'flags']:
                self.soledad.delete_doc.assert_any_call(doc)
        self.assertEqual(3, len(self.soledad.delete_doc.mock_calls))

    def _create_docs_of_type(self, type_list):
        return [self._create_doc_type(t) for t in type_list]

    def _create_doc_type(self, doc_type):
        doc = MagicMock(spec=SoledadDocument)
        doc.content = {'type': doc_type}
        return doc

    def test_load_mails_empty_path_list(self):
        load_mails(self.args, [])

        self.assertFalse(self.mailbox.called)

    def test_load_mails_adds_mails(self):
        # given
        mail_root = join(dirname(__file__), '..', 'fixtures', 'mailset')
        firstMailDeferred = defer.Deferred()
        secondMailDeferred = defer.Deferred()
        self.mailbox.addMessage.side_effect = [firstMailDeferred, secondMailDeferred]

        # when
        d = load_mails(self.args, [mail_root])

        # then
        def assert_mails_added(_):
            self.assertTrue(self.mailbox.addMessage.called)
            self.mailbox.addMessage.assert_any_call(self._mail_content(join(mail_root, 'new', 'mbox00000000')), flags=(WithMsgFields.RECENT_FLAG,), notify_on_disk=False)
            self.mailbox.addMessage.assert_any_call(self._mail_content(join(mail_root, 'new', 'mbox00000001')), flags=(WithMsgFields.RECENT_FLAG,), notify_on_disk=False)

        def error_callack(err):
            print err
            self.assertTrue(False)

        d.addCallback(assert_mails_added)
        d.addErrback(error_callack)

        # trigger callbacks for both mails
        reactor.callLater(0, firstMailDeferred.callback, None)
        reactor.callLater(0, secondMailDeferred.callback, None)

        return d

    def _mail_content(self, mail_file):
        with open(mail_file, 'r') as fp:
            m = email.message_from_file(fp)
            return m.as_string()
