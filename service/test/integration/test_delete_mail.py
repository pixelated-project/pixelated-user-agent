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
from twisted.internet import defer
from test.support.integration import SoledadTestBase, MailBuilder


class DeleteMailTest(SoledadTestBase):

    @defer.inlineCallbacks
    def test_move_mail_to_trash_when_deleting(self):
        input_mail = MailBuilder().with_subject('Mail with tags').build_input_mail()
        mail = yield self.app_test_client.add_mail_to_inbox(input_mail)

        inbox_mails = yield self.app_test_client.get_mails_by_tag('inbox')
        self.assertEquals(1, len(inbox_mails))

        yield self.app_test_client.delete_mail(mail.mail_id)

        inbox_mails = yield self.app_test_client.get_mails_by_tag('inbox')
        self.assertEquals(0, len(inbox_mails))
        trash_mails = yield self.app_test_client.get_mails_by_tag('trash')
        self.assertEquals(1, len(trash_mails))

    @defer.inlineCallbacks
    def test_delete_mail_when_trashing_mail_from_trash_mailbox(self):
        mails = yield self.app_test_client.add_multiple_to_mailbox(1, 'trash')
        yield self.app_test_client.delete_mails([mails[0].ident])

        trash_mails = yield self.app_test_client.get_mails_by_tag('trash')

        self.assertEqual(0, len(trash_mails))

    @defer.inlineCallbacks
    def test_move_mail_to_trash_when_delete_multiple(self):
        yield self.app_test_client.add_multiple_to_mailbox(1, 'trash')
        mails = yield self.app_test_client.add_multiple_to_mailbox(5, 'inbox')
        mail_idents = [m.ident for m in mails]

        yield self.app_test_client.delete_mails(mail_idents)

        inbox = yield self.app_test_client.get_mails_by_tag('inbox')
        self.assertEquals(0, len(inbox))

    @defer.inlineCallbacks
    def test_delete_permanently_when_mails_are_in_trash(self):
        mails = yield self.app_test_client.add_multiple_to_mailbox(5, 'trash')
        mail_idents = [m.ident for m in mails]

        yield self.app_test_client.delete_mails(mail_idents)

        trash = yield self.app_test_client.get_mails_by_tag('trash')
        self.assertEquals(0, len(trash))
