#  -*- coding: utf-8 -*-
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
# along with Pixelated. If not, see <http://www.gnu.org/licenses/>.
# You should have received a copy of the GNU Affero General Public License


from twisted.trial import unittest

from pixelated.support.functional import to_unicode


class UtilsTest(unittest.TestCase):

    def test_to_unicode_guesses_encoding_and_unicode_text(self):
        text = 'coração'
        self.assertEqual(u'coração', to_unicode(text))

    def test_to_unicode_self(self):
        text = u'already unicode'
        self.assertEqual(text, to_unicode(text))

    def test_to_unicode_empty_string(self):
        text = ''
        self.assertEqual(text, to_unicode(text))
