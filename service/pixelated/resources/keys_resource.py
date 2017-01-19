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

from email.utils import parseaddr
from pixelated.resources import respond_json_deferred, BaseResource
from twisted.web import server


class KeysResource(BaseResource):

    isLeaf = True

    def __init__(self, services_factory):
        BaseResource.__init__(self, services_factory)

    def render_GET(self, request):
        _keymanager = self.keymanager(request)

        def finish_request(key):
            if key.private:
                respond_json_deferred(None, request, status_code=401)
            else:
                respond_json_deferred(key.get_active_json(), request)

        def key_not_found(_):
            respond_json_deferred(None, request, status_code=404)

        _, key_to_find = parseaddr(request.args.get('search')[0])
        d = _keymanager.get_key(key_to_find)
        d.addCallback(finish_request)
        d.addErrback(key_not_found)

        return server.NOT_DONE_YET
