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

import json
from twisted.trial import unittest

from mock import patch, MagicMock
from mockito import mock, when, verify, any as ANY
from twisted.internet import defer
from twisted.web.test.requesthelper import DummyRequest

from pixelated.application import UserAgentMode
from pixelated.resources.attachments_resource import AttachmentsResource
from test.unit.resources import DummySite


class AttachmentsResourceTest(unittest.TestCase):

    def setUp(self):
        self.mail_service = mock()
        self.services_factory = mock()
        self.services_factory.mode = UserAgentMode(is_single_user=True)
        self.services = mock()
        self.services.mail_service = self.mail_service
        self.services_factory._services_by_user = {'someuserid': self.mail_service}
        when(self.services_factory).services(ANY()).thenReturn(self.services)

        self.mails_resource = AttachmentsResource(self.services_factory)
        self.mails_resource.isLeaf = True
        self.web = DummySite(self.mails_resource)

    @patch('cgi.FieldStorage')
    def test_post_new_attachment(self, mock_fields):
        request = DummyRequest(['/attachment'])
        request.method = 'POST'
        request.content = 'mocked'
        attachment_id = 'B5B4ED80AC3B894523D72E375DACAA2FC6606C18EDF680FE95903086C8B5E14A'
        _file = MagicMock()
        _file.value = 'some mocked value'
        _file.type = 'some mocked type'
        _file.filename = 'filename.txt'
        mock_fields.return_value = {'attachment': _file}
        when(self.mail_service).save_attachment('some mocked value', 'some mocked type').thenReturn(defer.succeed(attachment_id))

        d = self.web.get(request)

        def assert_response(_):
            self.assertEqual(201, request.code)
            self.assertEqual('/attachment/%s' % attachment_id, request.responseHeaders.getRawHeaders("location")[0])
            response_json = {'ident': attachment_id, 'content-type': 'some mocked type',
                             'name': 'filename.txt', 'size': 17, 'encoding': 'base64'}
            self.assertEqual(response_json, json.loads(request.written[0]))
            verify(self.mail_service).save_attachment('some mocked value', 'some mocked type')

        d.addCallback(assert_response)
        return d

    @patch('cgi.FieldStorage')
    def test_post_attachment_fails(self, mock_fields):
        request = DummyRequest(['/attachment'])
        request.method = 'POST'
        request.content = 'mocked'

        _file = MagicMock()
        _file.value = 'some mocked value'
        _file.type = 'some mocked type'
        mock_fields.return_value = {'attachment': _file}
        when(self.mail_service).save_attachment('some mocked value', 'some mocked type').thenReturn(defer.fail(Exception))

        d = self.web.get(request)

        def assert_response(_):
            self.assertEqual(500, request.code)
            self.assertFalse(request.responseHeaders.hasHeader('Location'.lower()))
            self.assertIn("message", json.loads(request.written[0]))
            verify(self.mail_service).save_attachment('some mocked value', 'some mocked type')

        d.addCallback(assert_response)
        return d
