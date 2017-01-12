# -*- coding: utf-8 -*-
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
from mock import patch
from pixelated.adapter.mailstore.body_parser import BodyParser


class BodyParserTest(unittest.TestCase):

    def test_simple_text(self):
        parser = BodyParser('simple text')

        self.assertEqual('simple text', parser.parsed_content())

    def test_base64_text(self):
        parser = BodyParser('dGVzdCB0ZXh0\n', content_type='text/plain; charset="utf-8"', content_transfer_encoding='base64')

        self.assertEqual('test text', parser.parsed_content())

    def test_8bit_transfer_encoding_with_iso_8859_1_str_input(self):
        data = 'Hmm, here are \xdcml\xe4\xfcts again!'
        parser = BodyParser(data, content_type='text/plain; charset=iso-8859-1', content_transfer_encoding='8bit')

        self.assertEqual(u'Hmm, here are Ümläüts again!', parser.parsed_content())

    def test_8bit_transfer_encoding_with_iso_8859_1_unicode_input(self):
        data = u'Hmm, here are \xdcml\xe4\xfcts again!'
        parser = BodyParser(data, content_type='text/plain; charset=iso-8859-1', content_transfer_encoding='8bit')

        self.assertEqual(u'Hmm, here are Ümläüts again!', parser.parsed_content())

    def test_base64_with_default_us_ascii_encoding(self):
        parser = BodyParser('dGVzdCB0ZXh0\n', content_type='text/plain', content_transfer_encoding='base64')

        self.assertEqual('test text', parser.parsed_content())

    @patch('pixelated.adapter.mailstore.body_parser.logger')
    def test_body_parser_logs_problems_and_then_ignores_invalid_chars(self, logger_mock):
        data = u'unkown char: \ufffd'
        parser = BodyParser(data, content_type='text/plain; charset=iso-8859-1', content_transfer_encoding='8bit')

        self.assertEqual(u'unkown char: ', parser.parsed_content())
        logger_mock.warn.assert_called_with(u'Failed to encode content for charset iso-8859-1. Ignoring invalid chars: \'latin-1\' codec can\'t encode character u\'\\ufffd\' in position 13: ordinal not in range(256)')

    def test_charset_can_be_explicitely_set_and_take_precedence_over_content_type_if_set(self):
        parser = BodyParser('YmzDoQ==\n', content_type='text/plain; us-ascii', content_transfer_encoding='base64',
                            charset="utf-8")

        self.assertEqual(u'bl\xe1', parser.parsed_content())
