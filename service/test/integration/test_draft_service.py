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


class DraftServiceTest(SoledadTestBase):

    @defer.inlineCallbacks
    def test_store_and_load_draft(self):
        input_mail = MailBuilder().with_body('some test text').build_input_mail()
        draft_id = None
        stored_draft = yield self.app_test_client.draft_service.process_draft(draft_id, input_mail)

        draft = yield self.app_test_client.mail_store.get_mail(stored_draft.ident, include_body=True)

        self.assertEqual('some test text', draft.body)

    @defer.inlineCallbacks
    def test_update_draft(self):
        input_mail = MailBuilder().with_body('some test text').build_input_mail()
        saved_mail = yield self.app_test_client.mail_store.add_mail('DRAFTS', input_mail.raw)
        draft_id = saved_mail.ident
        new_email = MailBuilder().with_body('other test text').with_ident(draft_id).build_input_mail()

        stored_draft = yield self.app_test_client.draft_service.process_draft(draft_id, new_email)

        old_draft = yield self.app_test_client.mail_store.get_mail(draft_id, include_body=True)
        draft = yield self.app_test_client.mail_store.get_mail(stored_draft.ident, include_body=True)

        self.assertIsNone(old_draft)
        self.assertEqual('other test text', draft.body)
