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

from pixelated.adapter.model.tag import Tag


class TestTag(unittest.TestCase):

    def test_from_dict_sets_all_tag_attributes(self):
        tag_dict = {'name': 'a_tag',
                    'default': False,
                    'counts': {'total': 3,
                               'read': 1,
                               'starred': 1,
                               'replied': 1},
                    'mails': [1, 2, 3]}

        tag = Tag.from_dict(tag_dict)

        self.assertEquals(tag_dict['name'], tag.name)
        self.assertEquals(tag_dict['default'], tag.default)
        self.assertEquals(tag_dict['counts']['total'], tag.total)
        # Checks if mail ids are aways restored as set()
        self.assertEquals(type(tag.mails), type(set()))
        self.assertEquals(set(tag_dict['mails']), tag.mails)

    def test_as_dict_puts_all_tag_attributes_in_the_returning_dict(self):
        tag = Tag('some_tag', default=True)
        tag.counts = {'total': 0, 'read': 0, 'starred': 0, 'replied': 0}
        tag.mails = [1, 2, 3]

        tag_dict = tag.as_dict()

        self.assertEquals(tag.name, tag_dict['name'])
        self.assertEquals(tag.default, tag_dict['default'])
        self.assertEquals(tag.total, tag_dict['counts']['total'])
        self.assertEquals(tag.mails, tag_dict['mails'])

    def test_increments_total_count_and_adds_mails_id_to_mails(self):
        tag = Tag('another')
        tag.increment(12)

        self.assertIn(12, tag.mails)
        self.assertEquals(1, tag.total)

    def test_decrement_does_nothing_if_mail_has_not_the_tag(self):
        tag = Tag('tag')
        tag.decrement(2000)

        self.assertEquals(0, tag.total)

    def test_increment_does_nothing_if_mail_already_has_the_tag(self):
        tag = Tag('tag')
        tag.mails = set([12])
        tag.increment(12)

        self.assertEquals(1, tag.total)

    def test_decrements_total_count_and_removes_mails_id_from_mails(self):
        tag = Tag('one_more')
        tag.mails = set([12])
        tag.decrement(12)

        self.assertNotIn(12, tag.mails)
        self.assertEquals(0, tag.total)
