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
from leap.soledad.common.document import SoledadDocument
from mockito import mock, when, unstub, verify
from twisted.internet import defer
from twisted.trial import unittest
from pixelated.adapter.search.index_storage_key import SearchIndexStorageKey
import os


class TestSearchIndexStorageKey(unittest.TestCase):

    def tearDown(self):
        unstub()

    @defer.inlineCallbacks
    def test_get_or_create_key_returns_key(self):
        soledad = mock()

        when(soledad).get_from_index(
            'by-type', 'index_key').thenReturn([SoledadDocument(json='{"value": "somekey"}')])

        key = yield SearchIndexStorageKey(soledad).get_or_create_key()

        self.assertEqual('somekey', key)

    @defer.inlineCallbacks
    def test_get_or_create_creates_key_if_not_exists(self):
        expected_key = '\x8brN\xa3\xe5-\x828 \x95\x8d\n\xc6\x0c\x82\n\xd7!\xa9\xb0.\xcc\\h\xa9\x98\xe9V\xc1*<\xfe\xbb\x8f\xcd\x7f\x8c#\xff\xf9\x840\xdf{}\x97\xebS-*\xe2f\xf9B\xa9\xb1\x0c\x1d-C)\xc5\xa0B'
        base64_encoded_key = 'i3JOo+UtgjgglY0KxgyCCtchqbAuzFxoqZjpVsEqPP67j81/jCP/+YQw33t9l+tTLSriZvlCqbEM\nHS1DKcWgQg==\n'
        soledad = mock()

        when(soledad).get_from_index('by-type', 'index_key').thenReturn([])
        when(os).urandom(64).thenReturn(expected_key)

        key = yield SearchIndexStorageKey(soledad).get_or_create_key()

        self.assertEqual(expected_key, key)

        verify(soledad).create_doc(
            dict(type='index_key', value=base64_encoded_key))
