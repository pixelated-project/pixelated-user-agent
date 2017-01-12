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
