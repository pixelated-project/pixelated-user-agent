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
from pixelated.adapter.listeners.mailbox_indexer_listener import MailboxIndexerListener
from test.support.integration import SoledadTestBase, MailBuilder
from twisted.internet import defer, reactor

IGNORED = None


class IncomingMailTest(SoledadTestBase):

    @defer.inlineCallbacks
    def test_message_collection(self):
        # given
        mail_collection = yield self.app_test_client.account.get_collection_by_mailbox('INBOX')
        input_mail = MailBuilder().build_input_mail()

        # when
        yield MailboxIndexerListener.listen(
            self.app_test_client.account,
            'INBOX',
            self.app_test_client.mail_store,
            self.app_test_client.search_engine)
        yield mail_collection.add_msg(input_mail.raw)

        # then
        yield self.wait_in_reactor()  # event handlers are called async, wait for it

        mails, mail_count = self.app_test_client.search_engine.search('in:all')
        self.assertEqual(1, mail_count)
        self.assertEqual(1, len(mails))

    def wait_in_reactor(self):
        d = defer.Deferred()

        def done_waiting():
            d.callback(None)

        reactor.callLater(1, done_waiting)
        return d
