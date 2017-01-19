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
