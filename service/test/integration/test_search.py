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


class SearchTest(SoledadTestBase):

    def test_that_tags_returns_all_tags(self):
        input_mail = MailBuilder().with_tags(['important']).build_input_mail()
        self.add_mail_to_inbox(input_mail)

        d = self.get_tags()

        def _assert(all_tags):
            all_tag_names = [t['name'] for t in all_tags]
            self.assertTrue('inbox' in all_tag_names)
            self.assertTrue('sent' in all_tag_names)
            self.assertTrue('trash' in all_tag_names)
            self.assertTrue('drafts' in all_tag_names)
            self.assertTrue('important' in all_tag_names)
        d.addCallback(_assert)
        return d

    def test_that_tags_are_filtered_by_query(self):
        input_mail = MailBuilder().with_tags(['ateu', 'catoa', 'luat', 'zuado']).build_input_mail()
        self.add_mail_to_inbox(input_mail)

        d = self.get_tags(q=["at"], skipDefaultTags=["true"])

        def _assert(all_tags):
            all_tag_names = [t['name'] for t in all_tags]
            self.assertEqual(3, len(all_tag_names))
            self.assertTrue('ateu' in all_tag_names)
            self.assertTrue('catoa' in all_tag_names)
            self.assertTrue('luat' in all_tag_names)

        d.addCallback(_assert)
        return d

    def test_tags_with_multiple_words_are_searchable(self):
        input_mail = MailBuilder().with_tags(['one tag four words']).build_input_mail()
        self.add_mail_to_inbox(input_mail)

        first_page = self.get_mails_by_tag('"one tag four words"', page=1, window=1)

        self.assertEqual(len(first_page), 1)

    def test_that_default_tags_are_ignorable(self):
        input_mail = MailBuilder().with_tags(['sometag']).build_input_mail()
        self.add_mail_to_inbox(input_mail)

        d = self.get_tags(skipDefaultTags=["true"])

        def _assert(all_tags):
            all_tag_names = [t['name'] for t in all_tags]
            self.assertEqual(1, len(all_tag_names))
            self.assertTrue('sometag' in all_tag_names)
        d.addCallback(_assert)
        return d

    def test_tags_count(self):
        self.add_multiple_to_mailbox(num=10, mailbox='inbox', flags=['\\Recent'])
        self.add_multiple_to_mailbox(num=5, mailbox='inbox', flags=['\\Seen'])
        self.add_multiple_to_mailbox(num=3, mailbox='inbox', flags=['\\Recent'], tags=['important', 'later'])
        self.add_multiple_to_mailbox(num=1, mailbox='inbox', flags=['\\Seen'], tags=['important'])

        d = self.get_tags()

        def _assert(tags_count):
            self.assertEqual(self.get_count(tags_count, 'inbox')['total'], 19)
            self.assertEqual(self.get_count(tags_count, 'inbox')['read'], 6)
            self.assertEqual(self.get_count(tags_count, 'important')['total'], 4)
            self.assertEqual(self.get_count(tags_count, 'important')['read'], 1)
        d.addCallback(_assert)
        return d

    def test_search_mails_different_window(self):
        input_mail = MailBuilder().build_input_mail()
        input_mail2 = MailBuilder().build_input_mail()
        self.add_mail_to_inbox(input_mail)
        self.add_mail_to_inbox(input_mail2)

        first_page = self.get_mails_by_tag('inbox', page=1, window=1)

        self.assertEqual(len(first_page), 1)

    def test_search_mails_with_multiple_pages(self):
        input_mail = MailBuilder().build_input_mail()
        input_mail2 = MailBuilder().build_input_mail()
        self.add_mail_to_inbox(input_mail)
        self.add_mail_to_inbox(input_mail2)

        first_page = self.get_mails_by_tag('inbox', page=1, window=1)
        second_page = self.get_mails_by_tag('inbox', page=2, window=1)

        idents = [input_mail.ident, input_mail2.ident]

        self.assertIn(first_page[0].ident, idents)
        self.assertIn(second_page[0].ident, idents)

    def test_page_zero_fetches_first_page(self):
        input_mail = MailBuilder().build_input_mail()
        self.add_mail_to_inbox(input_mail)
        page = self.get_mails_by_tag('inbox', page=0, window=1)
        self.assertEqual(page[0].ident, input_mail.ident)

    def get_count(self, tags_count, mailbox):
        for tag in tags_count:
            if tag['name'] == mailbox:
                return tag['counts']

    @defer.inlineCallbacks
    def test_order_by_date(self):
        input_mail = MailBuilder().with_date('2014-10-15T15:15').build_input_mail()
        input_mail2 = MailBuilder().with_date('2014-10-15T15:16').build_input_mail()

        yield self.add_mail_to_inbox(input_mail)
        yield self.add_mail_to_inbox(input_mail2)

        deferred = self.get_mails_by_tag('inbox')

        def _test(results):
            self.assertEqual(results[0].ident, input_mail2.ident)
            self.assertEqual(results[1].ident, input_mail.ident)

        deferred.addCallback(_test)

    def test_search_base64_body(self):
        body = u'bl\xe1'
        input_mail = MailBuilder().with_body(body.encode('utf-8')).build_input_mail()
        self.add_mail_to_inbox(input_mail)
        results = self.search(body)

        self.assertGreater(len(results), 0, 'No results returned from search')
        self.assertEquals(results[0].ident, input_mail.ident)
