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
import json
from mockito import mock, when, verify
from test.unit.resources import DummySite
from twisted.web.test.requesthelper import DummyRequest
from pixelated.resources.mails_resource import MailsArchiveResource
from twisted.internet import defer


class TestArchiveResource(unittest.TestCase):
    def setUp(self):
        self.mail_service = mock()
        self.web = DummySite(MailsArchiveResource(self.mail_service))

    def test_render_POST_should_archive_mails(self):
        request = DummyRequest(['/mails/archive'])
        request.method = 'POST'
        idents = ['1', '2']
        content = mock()
        when(content).read().thenReturn(json.dumps({'idents': ['1', '2']}))

        when(self.mail_service).archive_mail('1').thenReturn(defer.succeed(None))
        when(self.mail_service).archive_mail('2').thenReturn(defer.succeed(None))

        request.content = content
        d = self.web.get(request)

        def assert_response(_):
            verify(self.mail_service).archive_mail('1')
            verify(self.mail_service).archive_mail('2')

        d.addCallback(assert_response)
        return d
