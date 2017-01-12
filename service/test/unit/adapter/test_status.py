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

from pixelated.adapter.model.status import Status


class TestStatus(unittest.TestCase):

    def test_leap_seen_flag_is_translated_to_read_status(self):
        status = Status.from_flag('\\Seen')
        self.assertEquals('read', status)

    def test_leap_answered_flag_is_translated_to_replied_status(self):
        status = Status.from_flag('\\Answered')
        self.assertEquals('replied', status)

    def test_bulk_conversion(self):
        statuses = Status.from_flags(['\\Answered', '\\Seen', '\\Recent', 'tag_a_custom'])
        self.assertEquals(set(['read', 'replied', 'recent']), statuses)
