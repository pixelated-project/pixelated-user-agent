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
from twisted.trial.unittest import TestCase

from pixelated.adapter.mailstore.leap_mailstore import LeapMail, AttachmentInfo


class TestLeapMail(TestCase):
    def test_leap_mail(self):
        mail = LeapMail('', 'INBOX', {'From': 'test@example.test', 'Subject': 'A test Mail', 'To': 'receiver@example.test'})

        self.assertEqual('test@example.test', mail.from_sender)
        self.assertEqual(['receiver@example.test'], mail.to)
        self.assertEqual('A test Mail', mail.subject)

    def test_email_addresses_in_to_are_split_into_a_list(self):
        mail = LeapMail('', 'INBOX', {'To': 'first@example.test,second@example.test'})

        self.assertEqual(['first@example.test', 'second@example.test'], mail.headers['To'])

    def test_email_addresses_in_cc_are_split_into_a_list(self):
        mail = LeapMail('', 'INBOX', {'Cc': 'first@example.test,second@example.test'})

        self.assertEqual(['first@example.test', 'second@example.test'], mail.headers['Cc'])

    def test_email_addresses_in_bcc_are_split_into_a_list(self):
        mail = LeapMail('', 'INBOX', {'Bcc': 'first@example.test,second@example.test'})

        self.assertEqual(['first@example.test', 'second@example.test'], mail.headers['Bcc'])

    def test_email_addresses_might_be_empty_array(self):
        mail = LeapMail('', 'INBOX', {'Cc': None})

        self.assertEqual([], mail.headers['Cc'])

    def test_as_dict(self):
        mail = LeapMail('doc id', 'INBOX', {'From': 'test@example.test', 'Subject': 'A test Mail', 'To': 'receiver@example.test,receiver2@other.test'}, ('foo', 'bar'))
        self.maxDiff = None
        expected = {
            'header': {
                'from': 'test@example.test',
                'subject': 'A test Mail',
                'to': ['receiver@example.test', 'receiver2@other.test'],

            },
            'ident': 'doc id',
            'mailbox': 'inbox',
            'tags': {'foo', 'bar'},
            'status': [],
            'body': None,
            'textPlainBody': None,
            'security_casing': {
                'imprints': [{'state': 'no_signature_information'}],
                'locks': []
            },
            'replying': {'all': {'cc-field': [],
                                 'to-field': ['receiver@example.test',
                                              'test@example.test',
                                              'receiver2@other.test']},
                         'single': 'test@example.test'},
            'attachments': []
        }

        self.assertEqual(expected, mail.as_dict())

    def test_as_dict_with_body(self):
        body = 'some body content'
        mail = LeapMail('doc id', 'INBOX', {'From': 'test@example.test', 'Subject': 'A test Mail', 'To': 'receiver@example.test'}, ('foo', 'bar'), body=body)

        self.assertEqual(body, mail.as_dict()['body'])

    def test_as_dict_with_attachments(self):
        mail = LeapMail('doc id', 'INBOX', attachments=[AttachmentInfo('id', 'name', 'encoding')])

        self.assertEqual([{'ident': 'id', 'name': 'name', 'encoding': 'encoding'}],
                         mail.as_dict()['attachments'])

    def test_as_dict_headers_with_special_chars(self):
        expected_address = u'"\xc4lbert \xdcbr\xf6" <\xe4\xfc\xf6@example.mail>'
        expected_subject = u'H\xe4ll\xf6 W\xf6rld'
        mail = LeapMail('', 'INBOX',
                        {'From': '=?iso-8859-1?q?=22=C4lbert_=DCbr=F6=22_=3C=E4=FC=F6=40example=2Email=3E?=',
                         'To': '=?iso-8859-1?q?=22=C4lbert_=DCbr=F6=22_=3C=E4=FC=F6=40example=2Email=3E?=',
                         'Cc': '=?iso-8859-1?q?=22=C4lbert_=DCbr=F6=22_=3C=E4=FC=F6=40example=2Email=3E?=',
                         'Subject': '=?iso-8859-1?q?H=E4ll=F6_W=F6rld?='})

        self.assertEqual(expected_address, mail.as_dict()['header']['from'])
        self.assertEqual([expected_address], mail.as_dict()['header']['to'])
        self.assertEqual([expected_address], mail.as_dict()['header']['cc'])
        self.assertEqual(expected_subject, mail.as_dict()['header']['subject'])

    def test_as_dict_replying_with_special_chars(self):
        expected_address = u'"\xc4lbert \xdcbr\xf6" <\xe4\xfc\xf6@example.mail>'
        mail = LeapMail('', 'INBOX',
                        {'From': '=?iso-8859-1?q?=22=C4lbert_=DCbr=F6=22_=3C=E4=FC=F6=40example=2Email=3E?=',
                         'To': '=?iso-8859-1?q?=22=C4lbert_=DCbr=F6=22_=3C=E4=FC=F6=40example=2Email=3E?=',
                         'Cc': '=?iso-8859-1?q?=22=C4lbert_=DCbr=F6=22_=3C=E4=FC=F6=40example=2Email=3E?=',
                         'Subject': '=?iso-8859-1?q?H=E4ll=F6_W=F6rld?='})

        self.assertEqual([expected_address], mail.as_dict()['replying']['all']['to-field'])
        self.assertEqual([expected_address], mail.as_dict()['replying']['all']['cc-field'])
        self.assertEqual(expected_address, mail.as_dict()['replying']['single'])

    def test_as_dict_with_mixed_encodings(self):
        subject = 'Another test with =?iso-8859-1?B?3G1s5Px0?= =?iso-8859-1?Q?s?='
        mail = LeapMail('', 'INBOX',
                        {'Subject': subject})

        self.assertEqual(u'Another test with Ümläüts', mail.as_dict()['header']['subject'])

    def test_raw_constructed_by_headers_and_body(self):
        body = 'some body content'
        mail = LeapMail('doc id', 'INBOX', {'From': 'test@example.test', 'Subject': 'A test Mail', 'To': 'receiver@example.test'}, ('foo', 'bar'), body=body)

        result = mail.raw

        expected_raw = 'To: receiver@example.test\nFrom: test@example.test\nSubject: A test Mail\n\nsome body content'
        self.assertEqual(expected_raw, result)

    def test_headers_none_recipients_are_converted_to_empty_array(self):
        mail = LeapMail('id', 'INBOX', {'To': None, 'Cc': None, 'Bcc': None})

        self.assertEquals([], mail.headers['To'])
        self.assertEquals([], mail.headers['Cc'])
        self.assertEquals([], mail.headers['Bcc'])

    def test_security_casing(self):
        # No Encryption, no Signature
        mail = LeapMail('id', 'INBOX', {})
        self.assertEqual({'locks': [], 'imprints': [{'state': 'no_signature_information'}]}, mail.security_casing)

        # Encryption
        mail = LeapMail('id', 'INBOX', {'X-Leap-Encryption': 'decrypted'})
        self.assertEqual([{'state': 'valid'}], mail.security_casing['locks'])

        mail = LeapMail('id', 'INBOX', {'X-Leap-Encryption': 'false'})
        self.assertEqual([], mail.security_casing['locks'])

        # Signature
        mail = LeapMail('id', 'INBOX', {'X-Leap-Signature': 'valid'})
        self.assertEqual([{'seal': {'validity': 'valid'}, 'state': 'valid'}], mail.security_casing['imprints'])

        mail = LeapMail('id', 'INBOX', {'X-Leap-Signature': 'invalid'})
        self.assertEqual([], mail.security_casing['imprints'])
