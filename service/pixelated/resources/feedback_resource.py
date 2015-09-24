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

from twisted.web.resource import Resource
from pixelated.resources import respond_json


class FeedbackResource(Resource):
    isLeaf = True

    def __init__(self, feedback_service):
        Resource.__init__(self)
        self.feedback_service = feedback_service

    def render_POST(self, request):
        feedback = json.loads(request.content.read()).get('feedback')
        self.feedback_service.open_ticket(feedback)
        return respond_json({}, request)
