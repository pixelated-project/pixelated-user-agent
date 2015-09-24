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
# MERCHANTABILITY or FITNESS FOR A PCULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Pixelated. If not, see <http://www.gnu.org/licenses/>.
import json
import os
import re
import logging
import dateutil.parser as dateparser
from uuid import uuid4
from email import message_from_file
from email.mime.text import MIMEText
from email.header import decode_header, Header
from email.MIMEMultipart import MIMEMultipart
from pycryptopp.hash import sha256
from leap.mail.adaptors import soledad_indexes as fields
import leap.mail.walk as walk
from pixelated.adapter.model.status import Status
from pixelated.support import date
from pixelated.support.functional import compact

from twisted.internet import defer


logger = logging.getLogger(__name__)

TYPE_KEY = 'type'
CONTENT_HASH_KEY = 'chash'
HEADERS_KEY = 'headers'
DATE_KEY = 'date'
SUBJECT_KEY = 'subject'
PARTS_MAP_KEY = 'part_map'
BODY_KEY = 'body'
MSGID_KEY = 'msgid'
MULTIPART_KEY = 'multi'
SIZE_KEY = 'size'


class Mail(object):
    @property
    def from_sender(self):
        return self.headers['From']

    @property
    def to(self):
        return self.headers['To']

    @property
    def cc(self):
        return self.headers['Cc']

    @property
    def bcc(self):
        return self.headers['Bcc']

    @property
    def subject(self):
        return self.headers['Subject']

    @property
    def date(self):
        return self.headers['Date']

    @property
    def status(self):
        return Status.from_flags(self.flags)

    @property
    def flags(self):
        return self.fdoc.content.get('flags')

    @property
    def mailbox_name(self):
        # FIXME mbox is no longer available, instead we now have mbox_uuid
        return self.fdoc.content.get('mbox', 'INBOX')

    def _encode_header_value_list(self, header_value_list):
        return [self._encode_header_value(v) for v in header_value_list]

    def _encode_header_value(self, header_value):
        if isinstance(header_value, unicode):
            return str(Header(header_value, 'utf-8'))
        else:
            return str(header_value)

    @property
    def _mime_multipart(self):
        if self._mime:
            return self._mime
        mime = MIMEMultipart()
        for key, value in self.headers.items():
            if isinstance(value, list):
                mime[str(key)] = ', '.join(self._encode_header_value_list(value))
            else:
                mime[str(key)] = self._encode_header_value(value)

        try:
            body_to_use = self.body
        except AttributeError:
            body_to_use = self.text_plain_body

        mime.attach(MIMEText(body_to_use, 'plain', self._charset()))
        self._mime = mime
        return mime

    def _charset(self):
        if 'content_type' in self.headers and 'charset' in self.headers['content_type']:
            return self._parse_charset_header(self.headers['content_type'])
        else:
            return 'utf-8'

    def _parse_charset_header(self, charset_header, default_charset='utf-8'):
        try:
            return re.compile('.*charset=([a-zA-Z0-9-]+)', re.MULTILINE | re.DOTALL).match(charset_header).group(1)
        except:
            return default_charset

    @property
    def raw(self):
        return self._mime_multipart.as_string()

    def _get_chash(self):
        return sha256.SHA256(self.raw).hexdigest()


class InputMail(Mail):
    FROM_EMAIL_ADDRESS = None

    def __init__(self):
        self._raw_message = None
        self._fd = None
        self._hd = None
        self._bd = None
        self._chash = None
        self._mime = None
        self.headers = {}
        self.body = ''
        self._status = []

    @property
    def ident(self):
        return self._get_chash()

    def get_for_save(self, next_uid, mailbox):
        docs = [self._fdoc(next_uid, mailbox), self._hdoc()]
        docs.extend([m for m in self._cdocs()])
        return docs

    def _fdoc(self, next_uid, mailbox):
        if self._fd:
            return self._fd

        fd = {}
        fd[fields.MBOX] = mailbox
        fd[fields.MBOX_UUID] = next_uid
        fd[fields.CONTENT_HASH] = self._get_chash()
        fd[SIZE_KEY] = len(self.raw)
        fd[MULTIPART_KEY] = True
        fd[fields.RECENT] = True
        fd[fields.TYPE] = fields.FLAGS
        fd[fields.FLAGS] = Status.to_flags(self._status)
        self._fd = fd
        return fd

    def _get_body_phash(self):
        return walk.get_body_phash(self._mime_multipart)

    def _hdoc(self):
        if self._hd:
            return self._hd

        # InputMail does not have a from header but we need it when persisted into soledad.
        headers = self.headers.copy()
        headers['From'] = InputMail.FROM_EMAIL_ADDRESS

        hd = {}
        hd[HEADERS_KEY] = headers
        hd[DATE_KEY] = headers['Date']
        hd[CONTENT_HASH_KEY] = self._get_chash()
        hd[MSGID_KEY] = ''
        hd[MULTIPART_KEY] = True
        hd[SUBJECT_KEY] = headers.get('Subject')
        hd[TYPE_KEY] = fields.HEADERS
        hd[BODY_KEY] = self._get_body_phash()
        hd[PARTS_MAP_KEY] = \
            walk.walk_msg_tree(walk.get_parts(self._mime_multipart), body_phash=self._get_body_phash())['part_map']

        self._hd = hd
        return hd

    def _cdocs(self):
        return walk.get_raw_docs(self._mime_multipart, self._mime_multipart.walk())

    def to_mime_multipart(self):
        mime_multipart = MIMEMultipart()

        for header in ['To', 'Cc', 'Bcc']:
            if self.headers[header]:
                mime_multipart[header] = ", ".join(self.headers[header])

        if self.headers['Subject']:
            mime_multipart['Subject'] = self.headers['Subject']

        mime_multipart['Date'] = self.headers['Date']
        if type(self.body) is list:
            for part in self.body:
                mime_multipart.attach(MIMEText(part['raw'], part['content-type']))
        else:
            mime_multipart.attach(MIMEText(self.body, 'plain', 'utf-8'))
        return mime_multipart

    def to_smtp_format(self):
        mime_multipart = self.to_mime_multipart()
        mime_multipart['From'] = InputMail.FROM_EMAIL_ADDRESS
        return mime_multipart.as_string()

    @staticmethod
    def delivery_error_template(delivery_address):
        return InputMail.from_dict({
            'body': "Mail undelivered for %s" % delivery_address,
            'header': {
                'bcc': [],
                'cc': [],
                'subject': "Mail undelivered for %s" % delivery_address
            }
        })

    @staticmethod
    def from_dict(mail_dict):
        input_mail = InputMail()
        input_mail.headers = {key.capitalize(): value for key, value in mail_dict.get('header', {}).items()}

        input_mail.headers['Date'] = date.iso_now()

        input_mail.body = mail_dict.get('body', '')

        input_mail.tags = set(mail_dict.get('tags', []))

        input_mail._status = set(mail_dict.get('status', []))
        return input_mail

    @staticmethod
    def from_python_mail(mail):
        input_mail = InputMail()
        input_mail.headers = {key.capitalize(): value for key, value in mail.items()}
        input_mail.headers['Date'] = date.iso_now()
        input_mail.headers['Subject'] = mail['Subject']
        input_mail.headers['To'] = InputMail.FROM_EMAIL_ADDRESS
        input_mail._mime = MIMEMultipart()
        for payload in mail.get_payload():
            input_mail._mime.attach(payload)
            if payload.get_content_type() == 'text/plain':
                input_mail.body = payload.as_string()
        return input_mail


def welcome_mail():
    current_path = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_path, '..', '..', 'assets', 'welcome.mail')) as mail_template_file:
        mail_template = message_from_file(mail_template_file)
    return InputMail.from_python_mail(mail_template)
