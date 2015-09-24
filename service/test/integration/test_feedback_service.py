import os
import unittest
from mockito import when
from twisted.internet import defer
from test.support.integration import AppTestClient


class TestFeedbackService(unittest.TestCase, AppTestClient):
    @defer.inlineCallbacks
    def test_open_ticket(self):
        yield self.start_client()
        self.feedback_service.FEEDBACK_URL = "https://dev.pixelated-project.org/tickets"
        when(self.leap_session).account_email().thenReturn("text@pixelated-project.org")
        response = self.feedback_service.open_ticket("Pixelated is awesome!")

        self.assertEquals(response.status_code, 200)
