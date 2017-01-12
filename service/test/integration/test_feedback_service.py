from twisted.trial import unittest
from httmock import urlmatch, HTTMock
from mockito import when
from twisted.internet import defer
from test.support.integration import AppTestClient


@urlmatch(netloc=r'some.leap-provider.tld$')
def google_mock(url, request):
    return 'Pixelated is awesome!'


class TestFeedbackService(unittest.TestCase, AppTestClient):

    @defer.inlineCallbacks
    def test_open_ticket(self):
        with HTTMock(google_mock):
            yield self.start_client()
            self.feedback_service.FEEDBACK_URL = "https://some.leap-provider.tld/tickets"
            when(self.leap_session).account_email().thenReturn("text@pixelated-project.org")
            response = self.feedback_service.open_ticket("Pixelated is awesome!")

            self.assertEquals(response.status_code, 200)
