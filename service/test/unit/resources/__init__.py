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

from twisted.internet.defer import succeed
from twisted.web import server
from twisted.web.server import Site


def resolve_result(request, result):
    if isinstance(result, str):
        request.write(result)
        request.finish()
        return succeed(request)
    elif result is server.NOT_DONE_YET:
        if request.finished:
            return succeed(request)
        else:
            return request.notifyFinish().addCallback(lambda _: request)
    else:
        raise ValueError("Unexpected return value: %r" % (result,))


class DummySite(Site):
    def get(self, request):
        return resolve_result(request, self.getResourceFor(request).render(request))
