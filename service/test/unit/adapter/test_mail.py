# -*- coding: UTF-8 -*-
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
from email import message_from_file
from email.mime.nonmultipart import MIMENonMultipart
from email.mime.multipart import MIMEMultipart

from twisted.trial import unittest

import pixelated.support.date
from pixelated.adapter.model.mail import InputMail
import base64
import pkg_resources


def simple_mail_dict():
    return {
        'body': 'Este \xe9 o corpo',
        'header': {
            'cc': ['cc@pixelated.org', 'anothercc@pixelated.org'],
            'to': ['to@pixelated.org', 'anotherto@pixelated.org'],
            'bcc': ['bcc@pixelated.org', 'anotherbcc@pixelated.org'],
            'subject': 'Oi'
        },
        'ident': '',
        'tags': ['sent']
    }


def multipart_mail_dict():
    return {
        'body': [{'content-type': 'plain', 'raw': 'Hello world!'},
                 {'content-type': 'html', 'raw': '<p>Hello html world!</p>'}],
        'header': {
            'cc': ['cc@pixelated.org', 'anothercc@pixelated.org'],
            'to': ['to@pixelated.org', 'anotherto@pixelated.org'],
            'bcc': ['bcc@pixelated.org', 'anotherbcc@pixelated.org'],
            'subject': 'Oi',
        },
        'ident': '',
        'tags': ['sent']
    }


def with_attachment_mail_dict():
    return {
        'attachments': [{'content-type': 'text/plain', 'name': 'ayoyo.txt', 'raw': 'Hamburg Ayoyoyooooo!!!', 'ident': 'some_attachment_id'},
                        {'content-type': 'text/html', 'name': 'hello.html', 'raw': '<p>Hello html Hamburg!</p>', 'ident': 'other_attachment_id'}],
        'body': [{'content-type': 'plain', 'raw': 'Hello world!'},
                 {'content-type': 'html', 'raw': '<p>Hello html world!</p>'}],
        'header': {
            'cc': ['cc@pixelated.org', 'anothercc@pixelated.org'],
            'to': ['to@pixelated.org', 'anotherto@pixelated.org'],
            'bcc': ['bcc@pixelated.org', 'anotherbcc@pixelated.org'],
            'subject': 'Oi',
        },
        'ident': '',
        'tags': ['sent']
    }


class InputMailTest(unittest.TestCase):

    def test_to_mime_multipart_should_add_blank_fields(self):
        pixelated.support.date.mail_date_now = lambda: 'date now'

        mail_dict = simple_mail_dict()
        mail_dict['header']['to'] = ''
        mail_dict['header']['bcc'] = ''
        mail_dict['header']['cc'] = ''
        mail_dict['header']['subject'] = ''

        mime_multipart = InputMail.from_dict(mail_dict, from_address='pixelated@org').to_mime_multipart()

        self.assertNotRegexpMatches(mime_multipart.as_string(), "\nTo: \n")
        self.assertNotRegexpMatches(mime_multipart.as_string(), "\nBcc: \n")
        self.assertNotRegexpMatches(mime_multipart.as_string(), "\nCc: \n")
        self.assertNotRegexpMatches(mime_multipart.as_string(), "\nSubject: \n")

    def test_single_recipient(self):
        mail_single_recipient = {
            'body': '',
            'header': {
                'to': ['to@pixelated.org'],
                'cc': [''],
                'bcc': [''],
                'subject': 'Oi'
            }
        }

        result = InputMail.from_dict(mail_single_recipient, from_address='pixelated@org').raw

        self.assertRegexpMatches(result, 'To: to@pixelated.org')

    def test_to_mime_multipart(self):
        pixelated.support.date.mail_date_now = lambda: 'date now'

        mime_multipart = InputMail.from_dict(simple_mail_dict(), from_address='pixelated@org').to_mime_multipart()

        self.assertRegexpMatches(mime_multipart.as_string(), "\nTo: to@pixelated.org, anotherto@pixelated.org\n")
        self.assertRegexpMatches(mime_multipart.as_string(), "\nCc: cc@pixelated.org, anothercc@pixelated.org\n")
        self.assertRegexpMatches(mime_multipart.as_string(), "\nBcc: bcc@pixelated.org, anotherbcc@pixelated.org\n")
        self.assertRegexpMatches(mime_multipart.as_string(), "\nDate: date now\n")
        self.assertRegexpMatches(mime_multipart.as_string(), "\nSubject: Oi\n")
        self.assertRegexpMatches(mime_multipart.as_string(), base64.b64encode(simple_mail_dict()['body']))

    def test_to_mime_multipart_with_special_chars(self):
        mail_dict = simple_mail_dict()
        mail_dict['header']['to'] = u'"Älbert Übrö \xF0\x9F\x92\xA9" <äüö@example.mail>'
        pixelated.support.date.mail_date_now = lambda: 'date now'

        mime_multipart = InputMail.from_dict(mail_dict, from_address='pixelated@org').to_mime_multipart()

        expected_part_of_encoded_to = 'Iiwgw4QsIGwsIGIsIGUsIHIsIHQsICAsIMOcLCBiLCByLCDDtiwgICwgw7As'
        self.assertRegexpMatches(mime_multipart.as_string(), expected_part_of_encoded_to)

    def test_smtp_format(self):
        smtp_format = InputMail.from_dict(simple_mail_dict(), from_address='pixelated@org').to_smtp_format()

        self.assertRegexpMatches(smtp_format, "\nFrom: pixelated@org")

    def test_to_mime_multipart_handles_alternative_bodies(self):
        mime_multipart = InputMail.from_dict(multipart_mail_dict(), from_address='pixelated@org').to_mime_multipart()

        part_one = 'Content-Type: text/plain; charset="us-ascii"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\nHello world!'
        part_two = 'Content-Type: text/html; charset="us-ascii"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\n<p>Hello html world!</p>'

        self.assertRegexpMatches(mime_multipart.as_string(), part_one)
        self.assertRegexpMatches(mime_multipart.as_string(), part_two)

    def test_raw_with_attachment_data(self):
        input_mail = InputMail.from_dict(with_attachment_mail_dict(), from_address='pixelated@org')

        attachment = MIMENonMultipart('text', 'plain', Content_Disposition='attachment; filename=ayoyo.txt')
        attachment.set_payload('Hello World')
        mail = MIMEMultipart()
        mail.attach(attachment)

        part_one = 'Content-Type: text/plain\nMIME-Version: 1.0\nContent-Disposition: attachment; filename="ayoyo.txt"\nContent-Transfer-Encoding: base64\n\n'
        part_two = 'Content-Type: text/html\nMIME-Version: 1.0\nContent-Disposition: attachment; filename="hello.html"\nContent-Transfer-Encoding: base64\n\n'

        self.assertRegexpMatches(input_mail.raw, part_one)
        self.assertRegexpMatches(input_mail.raw, part_two)

    def test_charset_utf8(self):
        mail_file = pkg_resources.resource_filename('test.unit.fixtures', 'mail.utf8')
        with open(mail_file) as utf8_mail:
            mail = message_from_file(utf8_mail)
            input_mail = InputMail.from_python_mail(mail)
            body = u'utf8 é çñ\n'
            self.assertEqual(body, input_mail.body)

    def test_charset_latin1(self):
        mail_file = pkg_resources.resource_filename('test.unit.fixtures', 'mail.latin1')
        with open(mail_file) as latin1_mail:
            mail = message_from_file(latin1_mail)
            input_mail = InputMail.from_python_mail(mail)
            body = u'latin1 é çñ\n'
            self.assertEqual(body, input_mail.body)
