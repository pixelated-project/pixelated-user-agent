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
from test.support.integration import SoledadTestBase, MailBuilder
from twisted.internet import defer
import json
import pkg_resources


class ContactsTest(SoledadTestBase):

    @defer.inlineCallbacks
    def test_TO_CC_and_BCC_fields_are_being_searched(self):
        input_mail = MailBuilder().with_tags(['important']).build_input_mail()
        yield self.app_test_client.add_mail_to_inbox(input_mail)

        contacts = yield self.app_test_client.get_contacts(query='recipient')

        self.assertTrue('recipient@to.com' in contacts)
        self.assertTrue('recipient@cc.com' in contacts)
        self.assertTrue('recipient@bcc.com' in contacts)

    @defer.inlineCallbacks
    def test_FROM_address_is_being_searched(self):
        input_mail = MailBuilder().with_tags(['important']).with_from('Formatted Sender <sender@from.com>').build_input_mail()
        yield self.app_test_client.add_mail_to_inbox(input_mail)

        contacts = yield self.app_test_client.get_contacts(query='Sender')

        self.assertIn('Formatted Sender <sender@from.com>', contacts)

    @defer.inlineCallbacks
    def test_trash_and_drafts_mailboxes_are_being_ignored(self):
        yield self.app_test_client.add_multiple_to_mailbox(1, mailbox='INBOX', to='recipient@inbox.com')
        yield self.app_test_client.add_multiple_to_mailbox(1, mailbox='DRAFTS', to='recipient@drafts.com')
        yield self.app_test_client.add_multiple_to_mailbox(1, mailbox='SENT', to='recipient@sent.com')
        yield self.app_test_client.add_multiple_to_mailbox(1, mailbox='TRASH', to='recipient@trash.com')

        contacts = yield self.app_test_client.get_contacts(query='recipient')

        self.assertTrue('recipient@inbox.com' in contacts)
        self.assertTrue('recipient@sent.com' in contacts)
        self.assertFalse('recipient@drafts.com' in contacts)
        self.assertFalse('recipient@trash.com' in contacts)

    @defer.inlineCallbacks
    def test_deduplication_on_same_mail_address_using_largest(self):
        input_mail = MailBuilder().with_tags(['important']).with_from('sender@from.com').build_input_mail()

        formatted_input_mail = MailBuilder().with_tags(['important'])
        formatted_input_mail.with_to('Recipient Principal <recipient@to.com>')
        formatted_input_mail.with_cc('Recipient Copied <recipient@cc.com>')
        formatted_input_mail.with_bcc('Recipient Carbon <recipient@bcc.com>')
        formatted_input_mail = formatted_input_mail.build_input_mail()

        yield self.app_test_client.add_mail_to_inbox(input_mail)
        yield self.app_test_client.add_mail_to_inbox(formatted_input_mail)

        contacts = yield self.app_test_client.get_contacts(query='Recipient')

        self.assertEquals(4, len(contacts))
        self.assertTrue('Recipient Copied <recipient@cc.com>' in contacts)
        self.assertTrue('Recipient Carbon <recipient@bcc.com>' in contacts)
