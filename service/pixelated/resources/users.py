#
# Copyright (c) 2016 ThoughtWorks, Inc.
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

from pixelated.resources import respond_json_deferred, BaseResource, respond_json, UnAuthorizedResource
from twisted.web import server


class UsersResource(BaseResource):
    isLeaf = True

    def __init__(self, services_factory):
        BaseResource.__init__(self, services_factory)

    def render_GET(self, request):
        if self.is_admin(request):
            return respond_json(
                {"count": self._services_factory.online_sessions()}, request)
        return UnAuthorizedResource().render_GET(request)
