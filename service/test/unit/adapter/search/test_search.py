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
# You should have received a copy of the GNU Affero General Public License
# along with Pixelated. If not, see <http://www.gnu.org/licenses/>.


from twisted.trial import unittest
from pixelated.adapter.mailstore.leap_mailstore import LeapMail
from pixelated.adapter.search import SearchEngine
from tempdir import TempDir
from datetime import datetime
from test.support import test_helper

from pixelated.support.functional import to_unicode

INDEX_KEY = '\xde3?\x87\xff\xd9\xd3\x14\xf0\xa7>\x1f%C{\x16.\\\xae\x8c\x13\xa7\xfb\x04\xd4]+\x8d_\xed\xd1\x8d\x0bI' \
    '\x8a\x0e\xa4tm\xab\xbf\xb4\xa5\x99\x00d\xd5w\x9f\x18\xbc\x1d\xd4_W\xd2\xb6\xe8H\x83\x1b\xd8\x9d\xad'


class LockStub(object):
    def __init__(self):
        self.called = False

    def __enter__(self):
        self.called = True
        return self

    def __exit__(self, type, value, traceback):
        return False


class SearchEngineTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = TempDir()
        self.user_home = self.tempdir.name

    def tearDown(self):
        self.tempdir.dissolve()

    def test_headers_encoding(self):
        # given
        se = SearchEngine(INDEX_KEY, self.user_home)

        headers = {
            'From': 'foo@bar.tld',
            'To': '=?utf-8?b?IsOEw7zDtiDDlsO8w6QiIDxmb2xrZXJAcGl4ZWxhdGVkLXByb2plY3Qub3Jn?=\n =?utf-8?b?PiwgRsO2bGtlciA8Zm9sa2VyQHBpeGVsYXRlZC1wcm9qZWN0Lm9yZz4=?=',
            'Cc': '=?utf-8?b?IsOEw7zDtiDDlsO8w6QiIDxmb2xrZXJAcGl4ZWxhdGVkLXByb2plY3Qub3Jn?=\n =?utf-8?b?PiwgRsO2bGtlciA8Zm9sa2VyQHBpeGVsYXRlZC1wcm9qZWN0Lm9yZz4=?=',
            'Subject': 'Some test mail',
            'Date': str(datetime.now())
        }

        # when
        se.index_mail(LeapMail('mailid', 'INBOX', headers=headers))   # test_helper.pixelated_mail(extra_headers=headers, chash='mailid'))

        result = se.search('folker')

        self.assertEqual((['mailid'], 1), result)

    def test_contents_encoding_accents(self):
        # given
        se = SearchEngine(INDEX_KEY, self.user_home)

        headers = {
            'From': 'foo@bar.tld',
            'To': '=?utf-8?b?IsOEw7zDtiDDlsO8w6QiIDxmb2xrZXJAcGl4ZWxhdGVkLXByb2plY3Qub3Jn?=\n =?utf-8?b?PiwgRsO2bGtlciA8Zm9sa2VyQHBpeGVsYXRlZC1wcm9qZWN0Lm9yZz4=?=',
            'Cc': '=?utf-8?b?IsOEw7zDtiDDlsO8w6QiIDxmb2xrZXJAcGl4ZWxhdGVkLXByb2plY3Qub3Jn?=\n =?utf-8?b?PiwgRsO2bGtlciA8Zm9sa2VyQHBpeGVsYXRlZC1wcm9qZWN0Lm9yZz4=?=',
            'Subject': 'Some test mail',
            'Date': str(datetime.now())
        }

        body = "When doing the search, it's not possible to find words with graphical accents, e.g.: 'coração', 'é',  'Fièvre', La Pluie d'été, 'não'."

        # when
        se.index_mail(LeapMail('mailid', 'INBOX', headers=headers, body=body))   # test_helper.pixelated_mail(extra_headers=headers, chash='mailid'))

        result = se.search(u"'coração', 'é',")
        self.assertEqual((['mailid'], 1), result)

        result = se.search(u"Fièvre")
        self.assertEqual((['mailid'], 1), result)

        result = se.search(u"été")
        self.assertEqual((['mailid'], 1), result)

    def test_contents_encoding_special_characters(self):
        # given
        se = SearchEngine(INDEX_KEY, self.user_home)

        headers = {
            'From': 'foo@bar.tld',
            'To': '=?utf-8?b?IsOEw7zDtiDDlsO8w6QiIDxmb2xrZXJAcGl4ZWxhdGVkLXByb2plY3Qub3Jn?=\n =?utf-8?b?PiwgRsO2bGtlciA8Zm9sa2VyQHBpeGVsYXRlZC1wcm9qZWN0Lm9yZz4=?=',
            'Cc': '=?utf-8?b?IsOEw7zDtiDDlsO8w6QiIDxmb2xrZXJAcGl4ZWxhdGVkLXByb2plY3Qub3Jn?=\n =?utf-8?b?PiwgRsO2bGtlciA8Zm9sa2VyQHBpeGVsYXRlZC1wcm9qZWN0Lm9yZz4=?=',
            'Subject': 'Some test mail',
            'Date': str(datetime.now())
        }

        body = "When doing the search, 您好  أهلا"

        # when
        se.index_mail(LeapMail('mailid', 'INBOX', headers=headers, body=body))   # test_helper.pixelated_mail(extra_headers=headers, chash='mailid'))

        result = se.search(u"您好")
        self.assertEqual((['mailid'], 1), result)

        result = se.search(u"أهلا")
        self.assertEqual((['mailid'], 1), result)
