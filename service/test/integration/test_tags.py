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

from twisted.internet import defer

from test.support.integration import SoledadTestBase, MailBuilder
from pixelated.adapter.services.tag_service import SPECIAL_TAGS


class TagsTest(SoledadTestBase):

    def _tags_json(self, tags):
        return json.dumps({'newtags': tags})

    @defer.inlineCallbacks
    def test_add_tag_to_an_inbox_mail_and_query(self):
        input_mail = MailBuilder().with_subject('Mail with tags').build_input_mail()
        mail = yield self.app_test_client.add_mail_to_inbox(input_mail)

        yield self.app_test_client.post_tags(mail.ident, self._tags_json(['IMPORTANT']))

        mails = yield self.app_test_client.get_mails_by_tag('inbox')
        self.assertEquals({'IMPORTANT'}, set(mails[0].tags))

        mails = yield self.app_test_client.get_mails_by_tag('IMPORTANT')
        self.assertEquals('Mail with tags', mails[0].subject)

    @defer.inlineCallbacks
    def test_use_old_casing_when_same_tag_with_different_casing_is_posted(self):
        input_mail = MailBuilder().with_subject('Mail with tags').build_input_mail()
        mail = yield self.app_test_client.add_mail_to_inbox(input_mail)
        yield self.app_test_client.post_tags(mail.ident, self._tags_json(['ImPoRtAnT']))
        mails = yield self.app_test_client.get_mails_by_tag('ImPoRtAnT')
        self.assertEquals({'ImPoRtAnT'}, set(mails[0].tags))

        another_input_mail = MailBuilder().with_subject('Mail with tags').build_input_mail()
        another_mail = yield self.app_test_client.add_mail_to_inbox(another_input_mail)
        yield self.app_test_client.post_tags(another_mail.ident, self._tags_json(['IMPORTANT']))
        mails = yield self.app_test_client.get_mails_by_tag('IMPORTANT')
        self.assertEquals(0, len(mails))
        mails = yield self.app_test_client.get_mails_by_tag('ImPoRtAnT')
        self.assertEquals(2, len(mails))
        self.assertEquals({'ImPoRtAnT'}, set(mails[0].tags))
        self.assertEquals({'ImPoRtAnT'}, set(mails[1].tags))

    @defer.inlineCallbacks
    def test_tags_are_case_sensitive(self):
        input_mail = MailBuilder().with_subject('Mail with tags').build_input_mail()
        mail = yield self.app_test_client.add_mail_to_inbox(input_mail)

        yield self.app_test_client.post_tags(mail.ident, self._tags_json(['ImPoRtAnT']))

        mails = yield self.app_test_client.get_mails_by_tag('important')
        self.assertEquals(0, len(mails))

        mails = yield self.app_test_client.get_mails_by_tag('IMPORTANT')
        self.assertEquals(0, len(mails))

        mails = yield self.app_test_client.get_mails_by_tag('ImPoRtAnT')
        self.assertEquals({'ImPoRtAnT'}, set(mails[0].tags))

    @defer.inlineCallbacks
    def test_empty_tags_are_not_allowed(self):
        input_mail = MailBuilder().with_subject('Mail with tags').build_input_mail()
        mail = yield self.app_test_client.add_mail_to_inbox(input_mail)

        yield self.app_test_client.post_tags(mail.ident, self._tags_json(['tag1', '   ']))

        mail = yield self.app_test_client.get_mail(mail.ident)

        self.assertEquals(mail['tags'], ['tag1'])

    @defer.inlineCallbacks
    def test_addition_of_reserved_tags_is_not_allowed(self):
        input_mail = MailBuilder().with_subject('Mail with tags').build_input_mail()
        mail = yield self.app_test_client.add_mail_to_inbox(input_mail)

        for tag in SPECIAL_TAGS:
            response = yield self.app_test_client.post_tags(mail.ident, self._tags_json([tag.name.upper()]))
            self.assertEquals("None of the following words can be used as tags: %s" % tag.name, response)

        mail = yield self.app_test_client.mail_store.get_mail(mail.ident)
        self.assertNotIn('drafts', mail.tags)
