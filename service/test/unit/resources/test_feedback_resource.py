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
from mockito import verify, mock, when, any as ANY
from twisted.trial import unittest
from twisted.web.test.requesthelper import DummyRequest

from pixelated.application import UserAgentMode
from pixelated.resources.feedback_resource import FeedbackResource
from test.unit.resources import DummySite


class TestFeedbackResource(unittest.TestCase):
    def setUp(self):
        self.feedback_service = mock()
        self.services_factory = mock()
        self.services_factory.mode = UserAgentMode(is_single_user=True)
        self.services = mock()
        self.services.feedback_service = self.feedback_service
        self.services_factory._services_by_user = {'someuserid': self.feedback_service}
        when(self.services_factory).services(ANY()).thenReturn(self.services)

        self.web = DummySite(FeedbackResource(self.services_factory))

    def test_sends_feedback_to_leap_web(self):
        request = DummyRequest(['/feedback'])
        request.method = 'POST'
        content = mock()
        when(content).read().thenReturn(json.dumps({'feedback': 'Pixelated is awesome!'}))
        request.content = content

        d = self.web.get(request)

        def assert_posted_feedback_to_leap_web(_):
            verify(self.feedback_service).open_ticket('Pixelated is awesome!')

        d.addCallback(assert_posted_feedback_to_leap_web)
        return d
