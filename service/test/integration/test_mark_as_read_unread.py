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
from pixelated.adapter.model.status import Status


class MarkAsReadUnreadTest(SoledadTestBase):

    @defer.inlineCallbacks
    def test_mark_single_as_read(self):
        input_mail = MailBuilder().build_input_mail()
        mail = yield self.app_test_client.add_mail_to_inbox(input_mail)

        mails = yield self.app_test_client.get_mails_by_tag('inbox')
        self.assertNotIn('read', mails[0].status)

        yield self.app_test_client.mark_many_as_read([mail.ident])

        mails = yield self.app_test_client.get_mails_by_tag('inbox')
        self.assertIn('read', mails[0].status)

    @defer.inlineCallbacks
    def test_mark_single_as_unread(self):
        input_mail = MailBuilder().build_input_mail()
        mail = yield self.app_test_client.add_mail_to_inbox(input_mail)
        yield self.app_test_client.mark_many_as_read([mail.ident])

        yield self.app_test_client.mark_many_as_unread([mail.ident])
        result = (yield self.app_test_client.get_mails_by_tag('inbox'))[0]

        self.assertNotIn('read', result.status)

    @defer.inlineCallbacks
    def test_mark_many_mails_as_unread(self):
        input_mail = MailBuilder().with_status([Status.SEEN]).build_input_mail()
        input_mail2 = MailBuilder().with_status([Status.SEEN]).build_input_mail()

        mail1 = yield self.app_test_client.add_mail_to_inbox(input_mail)
        mail2 = yield self.app_test_client.add_mail_to_inbox(input_mail2)
        yield self.app_test_client.mark_many_as_read([mail1.ident, mail2.ident])

        yield self.app_test_client.mark_many_as_unread([mail1.ident, mail2.ident])

        mails = yield self.app_test_client.get_mails_by_tag('inbox')

        self.assertNotIn('read', mails[0].status)
        self.assertNotIn('read', mails[1].status)

    @defer.inlineCallbacks
    def test_mark_many_mails_as_read(self):
        input_mail = MailBuilder().build_input_mail()
        input_mail2 = MailBuilder().build_input_mail()

        yield self.app_test_client.add_mail_to_inbox(input_mail)
        yield self.app_test_client.add_mail_to_inbox(input_mail2)

        mails = yield self.app_test_client.get_mails_by_tag('inbox')

        self.assertNotIn('read', mails[0].status)
        self.assertNotIn('read', mails[1].status)

        yield self.app_test_client.mark_many_as_read([mails[0].ident, mails[1].ident])

        mails = yield self.app_test_client.get_mails_by_tag('inbox')

        self.assertIn('read', mails[0].status)
        self.assertIn('read', mails[1].status)

    @defer.inlineCallbacks
    def test_mark_mixed_status_as_read(self):
        input_mail = MailBuilder().with_subject('first').build_input_mail()
        input_mail2 = MailBuilder().with_subject('second').build_input_mail()

        yield self.app_test_client.add_mail_to_inbox(input_mail)
        mail2 = yield self.app_test_client.add_mail_to_inbox(input_mail2)
        yield self.app_test_client.mark_many_as_read([mail2.ident])

        mails = yield self.app_test_client.get_mails_by_tag('inbox')

        read_mails = filter(lambda x: 'read' in x.status, mails)
        unread_mails = filter(lambda x: 'read' not in x.status, mails)
        self.assertEquals(1, len(unread_mails))
        self.assertEquals(1, len(read_mails))

        yield self.app_test_client.mark_many_as_read([mails[0].ident, mails[1].ident])

        mails = yield self.app_test_client.get_mails_by_tag('inbox')

        self.assertIn('read', mails[0].status)
        self.assertIn('read', mails[1].status)
