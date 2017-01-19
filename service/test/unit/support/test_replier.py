#
# Copyright (c) 2015 ThoughtWorks, Inc.
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
from pixelated.support import replier


class TestReplier(unittest.TestCase):
    def test_reply_all_dont_exclude_own_address_if_only_recipient(self):
        current_user = sender = 'me@pixelated.org'
        to = [sender]
        cc = []

        reply_dict = replier.generate_recipients(sender, to, cc, current_user)
        expected = {'single': sender, 'all': {'to-field': [current_user], 'cc-field': []}}
        self.assertEquals(expected, reply_dict)

    def test_reply_all_does_not_contain_own_address_in_to(self):
        current_user = 'me@pixelated.org'
        sender = 'sender@pixelated.org'
        to = ['test@pixelated.org', current_user]
        cc = []

        reply_dict = replier.generate_recipients(sender, to, cc, current_user)
        expected = {'single': sender, 'all': {'to-field': ['test@pixelated.org', sender], 'cc-field': []}}
        self.assertEquals(expected, reply_dict)

    def test_reply_all_does_not_contain_own_address_in_cc(self):
        current_user = 'me@pixelated.org'
        sender = 'sender@pixelated.org'
        to = ['test@pixelated.org']
        cc = ['test2@pixelated.org', current_user]

        reply_dict = replier.generate_recipients(sender, to, cc, current_user)
        expected = {'single': sender, 'all': {'to-field': ['test@pixelated.org', sender], 'cc-field': ['test2@pixelated.org']}}
        self.assertEquals(expected, reply_dict)

    def test_reply_single_swaps_current_user_and_recipient_if_a_am_the_sender(self):
        current_user = sender = 'me@pixelated.org'
        to = ['test@pixelated.org']
        cc = []

        reply_dict = replier.generate_recipients(sender, to, cc, current_user)
        expected = {'single': 'test@pixelated.org', 'all': {'to-field': ['test@pixelated.org'], 'cc-field': []}}
        self.assertEquals(expected, reply_dict)
