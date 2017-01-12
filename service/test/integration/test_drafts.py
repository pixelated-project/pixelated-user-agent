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
from mockito import unstub, when, any
from twisted.internet import defer


class DraftsTest(SoledadTestBase):

    def tearDown(self):
        unstub()

    @defer.inlineCallbacks
    def test_post_sends_mail_and_deletes_previous_draft_if_it_exists(self):
        # act as if sending the mail by SMTP succeeded
        sendmail_deferred = defer.Deferred()
        when(self.app_test_client.mail_sender).sendmail(any()).thenReturn(sendmail_deferred)

        # creates one draft
        first_draft = MailBuilder().with_subject('First draft').build_json()
        first_draft_ident = (yield self.app_test_client.put_mail(first_draft)[0])['ident']

        # sends an updated version of the draft
        second_draft = MailBuilder().with_subject('Second draft').with_ident(first_draft_ident).build_json()
        deferred_res = self.post_mail(second_draft)

        sendmail_deferred.callback(None)  # SMTP succeeded

        yield deferred_res

        sent_mails = yield self.app_test_client.get_mails_by_tag('sent')
        drafts = yield self.app_test_client.get_mails_by_tag('drafts')

        # make sure there is one email in the sent mailbox and it is the second draft
        self.assertEquals(1, len(sent_mails))
        self.assertEquals('Second draft', sent_mails[0].subject)

        # make sure that there are no drafts in the draft mailbox
        self.assertEquals(0, len(drafts))

    @defer.inlineCallbacks
    def test_post_sends_mail_even_when_draft_does_not_exist(self):
        # act as if sending the mail by SMTP succeeded
        sendmail_deferred = defer.Deferred()
        when(self.app_test_client.mail_sender).sendmail(any()).thenReturn(sendmail_deferred)

        first_draft = MailBuilder().with_subject('First draft').build_json()
        res = self.post_mail(first_draft)
        sendmail_deferred.callback(True)
        yield res

        sent_mails = yield self.app_test_client.get_mails_by_tag('sent')
        drafts = yield self.app_test_client.get_mails_by_tag('drafts')

        self.assertEquals(1, len(sent_mails))
        self.assertEquals('First draft', sent_mails[0].subject)
        self.assertEquals(0, len(drafts))

    def post_mail(self, data):
        deferred_res, req = self.app_test_client.post('/mails', data)
        return deferred_res

    @defer.inlineCallbacks
    def test_put_creates_a_draft_if_it_does_not_exist(self):
        mail = MailBuilder().with_subject('A new draft').build_json()
        yield self.app_test_client.put_mail(mail)[0]
        mails = yield self.app_test_client.get_mails_by_tag('drafts')

        self.assertEquals('A new draft', mails[0].subject)

    @defer.inlineCallbacks
    def test_put_updates_draft_if_it_already_exists(self):
        draft = MailBuilder().with_subject('First draft').build_json()
        draft_ident = (yield self.app_test_client.put_mail(draft)[0])['ident']

        updated_draft = MailBuilder().with_subject('First draft edited').with_ident(draft_ident).build_json()
        yield self.app_test_client.put_mail(updated_draft)[0]

        drafts = yield self.app_test_client.get_mails_by_tag('drafts')

        self.assertEquals(1, len(drafts))
        self.assertEquals('First draft edited', drafts[0].subject)
