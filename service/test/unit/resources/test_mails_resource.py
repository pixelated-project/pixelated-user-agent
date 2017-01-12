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

from mock import patch
from mockito import mock, when, verify, any as ANY
from twisted.internet import defer
from twisted.web.test.requesthelper import DummyRequest

from pixelated.application import UserAgentMode
from pixelated.resources.mails_resource import MailsResource
from test.unit.resources import DummySite


class TestMailsResource(unittest.TestCase):
    def setUp(self):
        self.mail_service = mock()
        self.services_factory = mock()
        self.services_factory.mode = UserAgentMode(is_single_user=True)
        self.services = mock()
        self.services.mail_service = self.mail_service
        self.services.draft_service = mock()
        self.services_factory._services_by_user = {'someuserid': self.mail_service}
        when(self.services_factory).services(ANY()).thenReturn(self.services)

    @patch('leap.common.events.register')
    def test_render_GET_should_unicode_mails_search_query(self, mock_register):
        request = DummyRequest([])
        non_unicode_search_term = 'coração'
        request.addArg('q', non_unicode_search_term)
        request.addArg('w', 25)
        request.addArg('p', 1)

        unicodified_search_term = u'coração'
        when(self.mail_service).mails(unicodified_search_term, 25, 1).thenReturn(defer.succeed(([], 0)))

        mails_resource = MailsResource(self.services_factory)
        web = DummySite(mails_resource)
        d = web.get(request)

        def assert_response(_):
            verify(self.mail_service).mails(unicodified_search_term, 25, 1)

        d.addCallback(assert_response)
        return d

    @patch('leap.common.events.register')
    def test_render_PUT_should_store_draft_with_attachments(self, mock_register):
        request = DummyRequest([])
        request.method = 'PUT'
        request.content = mock()
        when(request.content).read().thenReturn('{"attachments": [{"ident": "some fake attachment id"}]}')
        when(self.mail_service).attachment('some fake attachment id').thenReturn(defer.succeed({'content': mock()}))

        mails_resource = MailsResource(self.services_factory)
        web = DummySite(mails_resource)
        d = web.get(request)

        def assert_response(_):
            verify(self.mail_service).attachment('some fake attachment id')

        d.addCallback(assert_response)
        return d

    @patch('leap.common.events.register')
    def test_render_POST_should_send_email_with_attachments(self, mock_register):
        request = DummyRequest([])
        request.method = 'POST'
        request.content = mock()
        when(request.content).read().thenReturn('{"attachments": [{"ident": "some fake attachment id"}]}')
        when(self.mail_service).attachment('some fake attachment id').thenReturn(defer.succeed({"content": "some content"}))
        as_dictable = mock()
        when(as_dictable).as_dict().thenReturn({})
        when(self.mail_service).send_mail({"attachments": [{"ident": "some fake attachment id", "raw": "some content"}]})\
            .thenReturn(defer.succeed(as_dictable))

        mails_resource = MailsResource(self.services_factory)
        web = DummySite(mails_resource)
        d = web.get(request)

        def assert_response(_):
            verify(self.mail_service).attachment('some fake attachment id')
            verify(self.mail_service).send_mail({"attachments": [{"ident": "some fake attachment id", "raw": "some content"}]})

        d.addCallback(assert_response)
        return d
