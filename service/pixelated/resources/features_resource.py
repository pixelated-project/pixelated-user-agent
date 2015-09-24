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

from pixelated.resources import respond_json
import os
from twisted.web.resource import Resource


class FeaturesResource(Resource):
    DISABLED_FEATURES = ['draftReply']
    isLeaf = True

    def render_GET(self, request):
        dispatcher_features = {}

        if os.environ.get('DISPATCHER_LOGOUT_URL'):
            dispatcher_features['logout'] = os.environ.get('DISPATCHER_LOGOUT_URL')

        if os.environ.get('FEEDBACK_URL') is None:
            self.DISABLED_FEATURES.append('feedback')

        return respond_json(
            {'disabled_features': self.DISABLED_FEATURES, 'dispatcher_features': dispatcher_features}, request)
