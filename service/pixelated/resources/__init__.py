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

import json
import os

from twisted.web.http import UNAUTHORIZED, BAD_REQUEST, INTERNAL_SERVER_ERROR, SERVICE_UNAVAILABLE
from twisted.web.resource import Resource
from twisted.logger import Logger
from twisted.cred.error import UnauthorizedLogin

from pixelated.resources.session import IPixelatedSession

log = Logger()


class InvalidPasswordError(Exception):
    pass


class EmptyFieldsError(Exception):
    pass


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return super(SetEncoder, self).default(obj)


def respond_json(entity, request, status_code=200):
    json_response = json.dumps(entity, cls=SetEncoder)
    request.responseHeaders.setRawHeaders(b"content-type", [b"application/json"])
    request.code = status_code
    return json_response


def respond_json_deferred(entity, request, status_code=200):
    json_response = json.dumps(entity, cls=SetEncoder)
    request.responseHeaders.setRawHeaders(b"content-type", [b"application/json"])
    request.code = status_code
    request.write(json_response)
    request.finish()


def handle_error_deferred(e, request):
    log.error(e)
    request.setResponseCode(INTERNAL_SERVER_ERROR)
    request.write('Something went wrong!')
    request.finish()


def get_protected_static_folder():
    return os.path.join(_get_static_folder(), 'protected')


def get_public_static_folder():
    return os.path.join(_get_static_folder(), 'public')


def _get_static_folder():
    static_folder = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", "..", "..", "web-ui", "dist"))
    if not os.path.exists(static_folder):
        static_folder = os.path.join('/', 'usr', 'share', 'pixelated-user-agent')
    return static_folder


def get_error_response_code(error_type):
    status_codes = {
        InvalidPasswordError: BAD_REQUEST,
        EmptyFieldsError: BAD_REQUEST,
        UnauthorizedLogin: UNAUTHORIZED
    }
    return status_codes.get(error_type, INTERNAL_SERVER_ERROR)


class BaseResource(Resource):

    def __init__(self, services_factory):
        Resource.__init__(self)
        self._services_factory = services_factory

    def _get_user_id_from_request(self, request):
        if self._services_factory.mode.is_single_user:
            return None  # it doesn't matter
        session = self.get_session(request)
        if session.is_logged_in():
            return session.user_uuid
        raise ValueError('Not logged in')

    def is_logged_in(self, request):
        session = self.get_session(request)
        return session.is_logged_in() and self._services_factory.has_session(session.user_uuid)

    def get_session(self, request):
        return IPixelatedSession(request.getSession())

    def is_admin(self, request):
        services = self._services(request)
        return services._leap_session.user_auth.is_admin()

    def _services(self, request):
        user_id = self._get_user_id_from_request(request)
        return self._services_factory.services(user_id)

    def _service(self, request, attribute):
        return getattr(self._services(request), attribute)

    def keymanager(self, request):
        return self._service(request, 'keymanager')

    def mail_service(self, request):
        return self._service(request, 'mail_service')

    def search_engine(self, request):
        return self._service(request, 'search_engine')

    def draft_service(self, request):
        return self._service(request, 'draft_service')

    def feedback_service(self, request):
        return self._service(request, 'feedback_service')

    def soledad(self, request):
        return self._service(request, '_leap_session').soledad


class UnAuthorizedResource(Resource):

    def __init__(self):
        Resource.__init__(self)

    def render_GET(self, request):
        request.setResponseCode(UNAUTHORIZED)
        return "Unauthorized!"

    def render_POST(self, request):
        request.setResponseCode(UNAUTHORIZED)
        return "Unauthorized!"


class UnavailableResource(Resource):
    def __init__(self):
        Resource.__init__(self)

    def render(self, request):
        request.setResponseCode(SERVICE_UNAVAILABLE)
        return "Service Unavailable"
