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
from twisted.trial import unittest
import email

from pixelated.maintenance import delete_all_mails, load_mails
from pixelated.config.sessions import LeapSession
from pixelated.adapter.mailstore import MailStore
from leap.soledad.client import Soledad
from leap.soledad.common.document import SoledadDocument
from mock import MagicMock
from os.path import join
from twisted.internet import defer
import pkg_resources


class TestCommands(unittest.TestCase):

    def setUp(self):
        self.leap_session = MagicMock(spec=LeapSession)
        self.soledad = MagicMock(spec=Soledad)
        self.mail_store = MagicMock(spec=MailStore)
        self.leap_session.mail_store = self.mail_store

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

        self.assertFalse(self.mail_store.add_mailbox.called)

    def test_load_mails_adds_mails(self):
        # given
        mail_root = pkg_resources.resource_filename('test.unit.fixtures', 'mailset')
        firstMailDeferred = defer.succeed(MagicMock())
        secondMailDeferred = defer.succeed(MagicMock())
        self.mail_store.add_mail.side_effect = [firstMailDeferred, secondMailDeferred]
        self.mail_store.add_mailbox.return_value = defer.succeed(None)

        # when
        d = load_mails(self.args, [mail_root])

        # then
        def assert_mails_added(_):
            self.assertTrue(self.mail_store.add_mail.called)
            self.mail_store.add_mail.assert_any_call('INBOX', self._mail_content(join(mail_root, 'new', 'mbox00000000')))
            self.mail_store.add_mail.assert_any_call('INBOX', self._mail_content(join(mail_root, 'new', 'mbox00000001')))
            # TODO Should we check for flags?

        def error_callack(err):
            print err
            self.assertTrue(False)

        d.addCallback(assert_mails_added)
        d.addErrback(error_callack)

        return d

    def test_load_mails_supports_mbox(self):
        # given
        mbox_file = pkg_resources.resource_filename('test.unit.fixtures', 'mbox')

        d = load_mails(self.args, [mbox_file])

        # then
        def assert_mails_added(_):
            self.assertTrue(self.mail_store.add_mail.called)
            self.mail_store.add_mail.assert_any_call('INBOX', self._mail_content(mbox_file))

        def error_callack(err):
            print err
            self.assertTrue(False)

        d.addCallback(assert_mails_added)
        d.addErrback(error_callack)

        return d

    def _mail_content(self, mail_file):
        with open(mail_file, 'r') as fp:
            m = email.message_from_file(fp)
            return m.as_string()
