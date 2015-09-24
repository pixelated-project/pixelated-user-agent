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
import json

from pixelated.adapter.model.mail import InputMail
from pixelated.adapter.model.status import Status


class MailBuilder:
    def __init__(self):
        self.mail = {
            'header': {
                'to': ['recipient@to.com'],
                'cc': ['recipient@cc.com'],
                'bcc': ['recipient@bcc.com'],
                'subject': 'Hi! This the subject'
            },
            'body': "Hello,\nThis is the body of this message\n\nRegards,\n\n--\nPixelated.\n",
            'status': []
        }
        InputMail.FROM_EMAIL_ADDRESS = 'Formatted Sender <sender@from.com>'

    def with_body(self, body):
        self.mail['body'] = body
        return self

    def with_tags(self, tags):
        self.mail['tags'] = tags
        return self

    def with_subject(self, subject):
        self.mail['header']['subject'] = subject
        return self

    def with_from(self, sender):
        self.mail['header']['from'] = sender
        return self

    def with_to(self, to):
        self.mail['header']['to'] = to
        return self

    def with_cc(self, cc):
        self.mail['header']['cc'] = cc
        return self

    def with_bcc(self, bcc):
        self.mail['header']['bcc'] = bcc
        return self

    def with_status(self, flags):
        for status in Status.from_flags(flags):
            self.mail['status'].append(status)
        return self

    def with_date(self, date_string):
        self.mail['header']['date'] = date_string
        return self

    def with_ident(self, ident):
        self.mail['ident'] = ident
        return self

    def build_json(self):
        return json.dumps(self.mail)

    def build_input_mail(self):
        return InputMail.from_dict(self.mail)

    def build_leap_mail(self):
        return LeapMail.from_dict(self.mail)


class ResponseMail:
    def __init__(self, mail_dict):
        self.mail_dict = mail_dict

    @property
    def subject(self):
        return self.headers['subject']

    @property
    def headers(self):
        return self.mail_dict['header']

    @property
    def ident(self):
        return self.mail_dict['ident']

    @property
    def tags(self):
        return self.mail_dict['tags']

    @property
    def status(self):
        return self.mail_dict['status']
