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

from mockito import mock, when, verify, any as ANY
from pixelated.adapter.listeners.mailbox_indexer_listener import MailboxIndexerListener
from twisted.internet import defer

from pixelated.adapter.listeners.mailbox_indexer_listener import logger


class MailboxListenerTest(unittest.TestCase):

    def setUp(self):
        self.mail_store = mock()
        self.account = mock()
        self.account.mailboxes = []

    def test_add_itself_to_mailbox_listeners(self):
        self.account.mailboxes = ['INBOX']
        mailbox = mock()
        when(self.account).get_collection_by_mailbox(
            'INBOX').thenReturn(mailbox)
        mailbox.listeners = set()
        when(mailbox).addListener = lambda x: mailbox.listeners.add(x)

        self.assertNotIn(MailboxIndexerListener(
            'INBOX', self.mail_store, mock()), mailbox.listeners)

        MailboxIndexerListener.listen(
            self.account, 'INBOX', self.mail_store, mock())

        self.assertIn(MailboxIndexerListener(
            'INBOX', self.mail_store, mock()), mailbox.listeners)

    def test_reindex_missing_idents(self):
        mail = mock()
        search_engine = mock()
        when(search_engine).search('tag:inbox',
                                   all_mails=True).thenReturn(['ident1', 'ident2'])

        listener = MailboxIndexerListener(
            'INBOX', self.mail_store, search_engine)
        when(self.mail_store).get_mailbox_mail_ids(
            'INBOX').thenReturn({'ident1', 'ident2', 'missing_ident'})
        when(self.mail_store).get_mails(
            {'missing_ident'}, include_body=True).thenReturn([mail])
        listener.notify_new()

        verify(self.mail_store, times=1).get_mails(
            {'missing_ident'}, include_body=True)
        verify(search_engine).index_mails([mail])

    @defer.inlineCallbacks
    def test_catches_exceptions_to_not_break_other_listeners(self):
        when(logger).error(ANY()).thenReturn(None)
        listener = MailboxIndexerListener('INBOX', self.mail_store, mock())

        yield listener.notify_new()

        verify(logger).error(ANY())
