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

from pixelated.adapter.search.contacts import address_duplication_filter
from pixelated.adapter.search.contacts import extract_mail_address


class TestContacts(unittest.TestCase):

    def test_contacts_filter_duplication_by_largest(self):
        contacts = ['John Large Name <john@name.example.com>', 'john@name.example.com', 'dont.delete@example.com']
        contacts_filtered = address_duplication_filter(contacts)
        self.assertIn('dont.delete@example.com', contacts_filtered)
        self.assertIn('John Large Name <john@name.example.com>', contacts_filtered)
        self.assertNotIn('john@name.example.com', contacts_filtered)

    def test_extract_mail_address_from_contact(self):
        full_address = 'John Large Name <john@name.example.com>'
        mail_address = 'john@name.example.com'

        self.assertEquals(mail_address, extract_mail_address(full_address))
