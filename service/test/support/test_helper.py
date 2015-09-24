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
from datetime import datetime
import io
from twisted.web.test.test_web import DummyRequest

from pixelated.adapter.model.mail import InputMail


LEAP_FLAGS = ['\\Seen',
              '\\Answered',
              '\\Flagged',
              '\\Deleted',
              '\\Draft',
              '\\Recent',
              'List']

DEFAULT_HEADERS = {'date': str(datetime.now())}


def mail_dict():
    return {
        'header': {
            'to': ['to@pixelated.org', 'anotherto@pixelated.org'],
            'cc': ['cc@pixelated.org', 'anothercc@pixelated.org'],
            'bcc': ['bcc@pixelated.org', 'anotherbcc@pixelated.org'],
            'subject': 'Subject'
        },
        'body': 'Body',
        'ident': '',
        'tags': []
    }


class TestDoc(object):
    def __init__(self, content):
        self.content = content

    def __getitem__(self, key):
        return self.content[key]


def leap_mail(uid=0, flags=LEAP_FLAGS, headers=None, extra_headers={}, mbox_uuid='INBOX', body='body',
              chash='chash'):
    fdoc = TestDoc({'flags': flags, 'mbox_uuid': mbox_uuid, 'type': 'flags', 'uid': uid, 'chash': chash})

    if headers is None:
        headers = {}
    if not (headers.get('received') or headers.get('date')):
        headers.update(DEFAULT_HEADERS)
    headers['headers'] = extra_headers
    hdoc = TestDoc(headers)

    bdoc = TestDoc({'raw': body, 'type': 'cnt'})

    return (fdoc, hdoc, bdoc)


def input_mail():
    mail = InputMail()
    mail.fdoc = TestDoc({})
    mail._chash = "123"
    mail.as_dict = lambda: None
    return mail


class TestRequest:

    def __init__(self, json):
        self.json = json


class PixRequestMock(DummyRequest):
    def __init__(self, path):
        DummyRequest.__init__(self, path)
        self.content = None
        self.code = None

    def getWrittenData(self):
        if len(self.written):
            return self.written[0]


def request_mock(path='', method='GET', body='', headers={}):
    dummy = PixRequestMock(path.split('/'))
    for name, value in headers.iteritems():
        dummy.setHeader(name, value)
    dummy.method = method
    dummy.content = io.BytesIO(body)
    return dummy
