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
from uuid import uuid4
from email.mime.text import MIMEText
from email.header import decode_header

from leap.mail.adaptors import soledad_indexes as fields
import leap.mail.walk as walk
import dateutil.parser as dateparser
from datetime import datetime
from pixelated.adapter.model.status import Status
import pixelated.support.date
from email.MIMEMultipart import MIMEMultipart
from pycryptopp.hash import sha256
import re
from pixelated.support.functional import compact
import logging


logger = logging.getLogger(__name__)


class Mail(object):
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
        return self.fdoc.content.get('mbox')

    @property
    def _mime_multipart(self):
        if self._mime:
            return self._mime
        mime = MIMEMultipart()
        for key, value in self.headers.items():
            mime[str(key)] = str(value)

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
        fd[fields.MBOX_KEY] = mailbox
        fd[fields.UID_KEY] = next_uid
        fd[fields.CONTENT_HASH_KEY] = self._get_chash()
        fd[fields.SIZE_KEY] = len(self.raw)
        fd[fields.MULTIPART_KEY] = True
        fd[fields.RECENT_KEY] = True
        fd[fields.TYPE_KEY] = fields.TYPE_FLAGS_VAL
        fd[fields.FLAGS_KEY] = Status.to_flags(self._status)
        self._fd = fd
        return fd

    def _get_body_phash(self):
        return walk.get_body_phash_multi(walk.get_payloads(self._mime_multipart))

    def _hdoc(self):
        if self._hd:
            return self._hd

        # InputMail does not have a from header but we need it when persisted into soledad.
        headers = self.headers.copy()
        headers['From'] = InputMail.FROM_EMAIL_ADDRESS

        hd = {}
        hd[fields.HEADERS_KEY] = headers
        hd[fields.DATE_KEY] = headers['Date']
        hd[fields.CONTENT_HASH_KEY] = self._get_chash()
        hd[fields.MSGID_KEY] = ''
        hd[fields.MULTIPART_KEY] = True
        hd[fields.SUBJECT_KEY] = headers.get('Subject')
        hd[fields.TYPE_KEY] = fields.TYPE_HEADERS_VAL
        hd[fields.BODY_KEY] = self._get_body_phash()
        hd[fields.PARTS_MAP_KEY] = \
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

        # XXX this is overriding the property in PixelatedMail
        input_mail.headers['Date'] = pixelated.support.date.iso_now()

        # XXX this is overriding the property in PixelatedMail
        input_mail.body = mail_dict.get('body', '')

        # XXX this is overriding the property in the PixelatedMail
        input_mail.tags = set(mail_dict.get('tags', []))

        input_mail._status = set(mail_dict.get('status', []))
        return input_mail


class PixelatedMail(Mail):

    @staticmethod
    def from_soledad(fdoc, hdoc, bdoc, parts=None, soledad_querier=None):
        mail = PixelatedMail()
        mail.parts = parts
        mail.boundary = str(uuid4()).replace('-', '')
        mail.bdoc = bdoc
        mail.fdoc = fdoc
        mail.hdoc = hdoc
        mail.querier = soledad_querier
        mail._mime = None
        return mail

    def _decode_part(self, part):
        encoding = part['headers'].get('Content-Transfer-Encoding', '')
        content_type = self._parse_charset_header(part['headers'].get('Content-Type'))

        try:
            decoding_func = self._decoding_function_for_encoding(encoding)
            return self._decode_content_with_fallback(part['content'], decoding_func, content_type)
        except Exception:
            logger.error('Failed to decode mail part with:')
            logger.error('Content-Transfer-Encoding: %s' % encoding)
            logger.error('Content-Type: %s' % part['headers'].get('Content-Type'))
            raise

    def _decoding_function_for_encoding(self, encoding):
        decoding_map = {
            'quoted-printable': lambda content, content_type: content.decode('quopri').decode(content_type),
            'base64': lambda content, content_type: content.decode('base64').decode('utf-8'),
            '7bit': lambda content, content_type: content.encode(content_type),
            '8bit': lambda content, content_type: content.encode(content_type)
        }
        if encoding in decoding_map:
            return decoding_map[encoding]
        else:
            return decoding_map['8bit']

    def _decode_content_with_fallback(self, content, decode_func, content_type):
        try:
            return decode_func(content, content_type)
            # return content.encode(content_type)
        except ValueError:
            return content.encode('ascii', 'ignore')

    @property
    def alternatives(self):
        return self.parts.get('alternatives')

    @property
    def text_plain_body(self):
        if self.parts and len(self.alternatives) >= 1:
            return self._decode_part(self.alternatives[0])
        else:
            return self.bdoc.content['raw']  # plain

    @property
    def html_body(self):
        if self.parts and len(self.alternatives) > 1:
            html_parts = [e for e in self.alternatives if re.match('text/html', e['headers'].get('Content-Type', ''))]
            if len(html_parts):
                return self._decode_part(html_parts[0])

    @property
    def headers(self):
        _headers = {
            'To': [],
            'Cc': [],
            'Bcc': []
        }
        hdoc_headers = self.hdoc.content['headers']

        for header in ['To', 'Cc', 'Bcc']:
            header_value = self._decode_header(hdoc_headers.get(header))
            if not header_value:
                continue
            _headers[header] = header_value if type(header_value) is list else header_value.split(',')
            _headers[header] = [head.strip() for head in compact(_headers[header])]

        for header in ['From', 'Subject']:
            _headers[header] = self._decode_header(hdoc_headers.get(header))

        try:
            _headers['Date'] = self._get_date()
        except Exception, e:
            _headers['Date'] = pixelated.support.date.iso_now()

        if self.parts and len(self.parts['alternatives']) > 1:
            _headers['content_type'] = 'multipart/alternative; boundary="%s"' % self.boundary
        elif self.hdoc.content['headers'].get('Content-Type'):
            _headers['content_type'] = hdoc_headers.get('Content-Type')

        if hdoc_headers.get('Reply-To'):
            _headers['Reply-To'] = hdoc_headers.get('Reply-To')

        return _headers

    def _decode_header_with_fallback(self, entry):
        try:
            return decode_header(entry)[0][0]
        except Exception, e:
            return entry.encode('ascii', 'ignore')

    def _decode_header(self, header):
        if not header:
            return None
        if isinstance(header, list):
            return [self._decode_header_with_fallback(entry) for entry in header]
        else:
            return self._decode_header_with_fallback(header)

    def _get_date(self):
        date = self.hdoc.content.get('date', None)
        try:
            if not date:
                received = self.hdoc.content.get('received', None)
                if received:
                        date = received.split(";")[-1].strip()
                else:
                    # we can't get a date for this mail, so lets just use now
                    logger.warning('Encountered a mail with missing date and received header fields. ID %s' % self.fdoc.content.get('uid', None))
                    date = pixelated.support.date.iso_now()
            return dateparser.parse(date).isoformat()
        except (ValueError, TypeError) as e:
            date = pixelated.support.date.iso_now()
            return dateparser.parse(date).isoformat()

    @property
    def security_casing(self):
        casing = {"imprints": [], "locks": []}
        casing["imprints"] = self.signature_information
        if self.encrypted == "true":
            casing["locks"] = [{"state": "valid"}]
        elif self.encrypted == "fail":
            casing["locks"] = [{"state": "failure"}]
        return casing

    @property
    def tags(self):
        _tags = self.fdoc.content.get('tags', '[]')
        return set(_tags) if type(_tags) is list or type(_tags) is set else set(json.loads(_tags))

    @property
    def ident(self):
        return self.fdoc.content.get('chash')

    @property
    def mailbox_name(self):
        return self.fdoc.content.get('mbox')

    @property
    def is_recent(self):
        return Status('recent') in self.status

    @property
    def uid(self):
        return self.fdoc.content['uid']

    def save(self):
        return self.querier.save_mail(self)

    def set_mailbox(self, mailbox_name):
        self.fdoc.content['mbox'] = mailbox_name

    def remove_all_tags(self):
        self.update_tags(set([]))

    def update_tags(self, tags):
        self._persist_mail_tags(tags)
        return self.tags

    def mark_as_read(self):
        if Status.SEEN in self.fdoc.content['flags']:
            return self
        self.fdoc.content['flags'].append(Status.SEEN)
        self.save()
        return self

    def mark_as_unread(self):
        if Status.SEEN in self.fdoc.content['flags']:
            self.fdoc.content['flags'].remove(Status.SEEN)
            self.save()
        return self

    def mark_as_not_recent(self):
        if Status.RECENT in self.fdoc.content['flags']:
            self.fdoc.content['flags'].remove(Status.RECENT)
            self.save()
        return self

    def _persist_mail_tags(self, current_tags):
        self.fdoc.content['tags'] = json.dumps(list(current_tags))
        self.save()

    def has_tag(self, tag):
        return tag in self.tags

    @property
    def signature_information(self):
        signature = self.hdoc.content["headers"].get("X-Leap-Signature", None)
        if signature is None or signature.startswith("could not verify"):
            return [{"state": "no_signature_information"}]
        else:
            if signature.startswith("valid"):
                return [{"state": "valid", "seal": {"validity": "valid"}}]
            else:
                return []

    @property
    def encrypted(self):
        return self.hdoc.content["headers"].get("X-Pixelated-encryption-status", "false")

    @property
    def bounced(self):
        content_type = self.hdoc.content["headers"].get("Content-Type", '')
        if re.compile('delivery-status').search(content_type):
            bounce_recipient = self._extract_bounced_address(self.hdoc.content)
            bounce_daemon = self.headers["From"]
            return [bounce_recipient, bounce_daemon] if bounce_recipient else False

        return False

    def _extract_bounced_address(self, part):
        part_header = dict(part.get('headers', {}))
        if 'Final-Recipient' in part_header:
            if self._bounce_permanent(part_header):
                return part_header['Final-Recipient'].split(';')[1].strip()
            else:
                return False
        elif 'part_map' in part:
            for subpart in part['part_map'].values():
                result = self._extract_bounced_address(subpart)
                if result:
                    return result
                else:
                    continue
        return False

    def _bounce_permanent(self, part_headers):
        status = part_headers.get('Status', '')
        return status.startswith('5')

    def as_dict(self):
        dict_mail = {'header': {k.lower(): v for k, v in self.headers.items()},
                     'ident': self.ident,
                     'tags': list(self.tags),
                     'status': list(self.status),
                     'security_casing': self.security_casing,
                     'textPlainBody': self.text_plain_body,
                     'htmlBody': self.html_body,
                     'mailbox': self.mailbox_name.lower(),
                     'attachments': self.parts['attachments'] if self.parts else []}
        dict_mail['replying'] = {'single': None, 'all': {'to-field': [], 'cc-field': []}}

        sender_mail = self.headers.get('Reply-To', self.headers.get('From'))
        # Issue #215: Fix for existing mails without any from address.
        if sender_mail is None:
            sender_mail = InputMail.FROM_EMAIL_ADDRESS

        recipients = [recipient for recipient in self.headers['To'] if recipient != InputMail.FROM_EMAIL_ADDRESS]
        recipients.append(sender_mail)
        ccs = [cc for cc in self.headers['Cc'] if cc != InputMail.FROM_EMAIL_ADDRESS]

        dict_mail['replying']['single'] = sender_mail
        dict_mail['replying']['all']['to-field'] = recipients
        dict_mail['replying']['all']['cc-field'] = ccs
        return dict_mail
