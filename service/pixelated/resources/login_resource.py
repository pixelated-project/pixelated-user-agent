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

import os
from xml.sax import SAXParseException

from pixelated.authentication import Authenticator
from pixelated.config.leap import BootstrapUserServices
from pixelated.resources import BaseResource, UnAuthorizedResource, IPixelatedSession
from pixelated.resources import handle_error_deferred
from twisted.internet import defer
from twisted.logger import Logger
from twisted.python.filepath import FilePath
from twisted.web import util
from twisted.web.http import UNAUTHORIZED, OK
from twisted.web.resource import NoResource
from twisted.web.server import NOT_DONE_YET
from twisted.web.static import File
from twisted.web.template import Element, XMLFile, renderElement, renderer

log = Logger()


def _get_startup_folder():
    path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(path, '..', 'assets')


def _get_static_folder():
    static_folder = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", "..", "web-ui", "dist"))
    # this is a workaround for packaging
    if not os.path.exists(static_folder):
        static_folder = os.path.abspath(
            os.path.join(os.path.abspath(__file__), "..", "..", "..", "..", "web-ui", "dist"))
    if not os.path.exists(static_folder):
        static_folder = os.path.join('/', 'usr', 'share', 'pixelated-user-agent')
    return static_folder


def parse_accept_language(all_headers):
    accepted_languages = ['pt-BR', 'en-US']
    languages = all_headers.get('accept-language', '').split(';')[0]
    for language in accepted_languages:
        if language in languages:
            return language
    return 'pt-BR'


class DisclaimerElement(Element):
    loader = XMLFile(FilePath(os.path.join(_get_startup_folder(), '_login_disclaimer_banner.html')))

    def __init__(self, banner):
        super(DisclaimerElement, self).__init__()
        self._set_loader(banner)
        self._banner_filename = banner or "_login_disclaimer_banner.html"

    def _set_loader(self, banner):
        if banner:
            current_path = os.path.dirname(os.path.abspath(__file__))
            banner_file_path = os.path.join(current_path, "..", "..", "..", banner)
            self.loader = XMLFile(FilePath(banner_file_path))

    def render(self, request):
        try:
            return super(DisclaimerElement, self).render(request)
        except SAXParseException:
            return ["Invalid XML template format for %s." % self._banner_filename]
        except IOError:
            return ["Disclaimer banner file %s could not be read or does not exit." % self._banner_filename]


class LoginWebSite(Element):
    loader = XMLFile(FilePath(os.path.join(_get_startup_folder(), 'login.html')))

    def __init__(self, error_msg=None, disclaimer_banner_file=None):
        super(LoginWebSite, self).__init__()
        self._error_msg = error_msg
        self.disclaimer_banner_file = disclaimer_banner_file

    @renderer
    def error_msg(self, request, tag):
        if self._error_msg is not None:
            return tag(self._error_msg)
        return tag('')

    @renderer
    def disclaimer(self, request, tag):
        return DisclaimerElement(self.disclaimer_banner_file).render(request)


class LoginResource(BaseResource):
    BASE_URL = 'login'

    def __init__(self, services_factory, provider=None, disclaimer_banner=None, authenticator=None):
        BaseResource.__init__(self, services_factory)
        self._static_folder = _get_static_folder()
        self._startup_folder = _get_startup_folder()
        self._disclaimer_banner = disclaimer_banner
        self._provider = provider
        self._authenticator = authenticator or Authenticator(provider)
        self._bootstrap_user_services = BootstrapUserServices(services_factory, provider)

        self.putChild('startup-assets', File(self._startup_folder))
        with open(os.path.join(self._startup_folder, 'Interstitial.html')) as f:
            self.interstitial = f.read()

    def getChild(self, path, request):
        if path == '':
            return self
        if path == 'login':
            return self
        if not self.is_logged_in(request):
            return UnAuthorizedResource()
        return NoResource()

    def render_GET(self, request):
        request.setResponseCode(OK)
        return self._render_template(request)

    def _render_template(self, request, error_msg=None):
        site = LoginWebSite(error_msg=error_msg, disclaimer_banner_file=self._disclaimer_banner)
        return renderElement(request, site)

    def render_POST(self, request):
        if self.is_logged_in(request):
            return util.redirectTo("/", request)

        def render_response(user_auth):
            request.setResponseCode(OK)
            request.write(self.interstitial)
            request.finish()
            self._complete_bootstrap(user_auth, request)

        def render_error(error):
            log.info('Login error for %s' % request.args['username'][0])
            log.info('%s' % error)
            request.setResponseCode(UNAUTHORIZED)
            return self._render_template(request, 'Invalid username or password')

        d = self._handle_login(request)
        d.addCallbacks(render_response, render_error)
        d.addErrback(handle_error_deferred, request)

        return NOT_DONE_YET

    @defer.inlineCallbacks
    def _handle_login(self, request):
        username = request.args['username'][0]
        password = request.args['password'][0]
        user_auth = yield self._authenticator.authenticate(username, password)
        defer.returnValue(user_auth)

    def _complete_bootstrap(self, user_auth, request):
        def log_error(error):
            log.error('Login error during %s services setup: %s \n %s' % (user_auth.username, error.getErrorMessage(), error.getTraceback()))

        def set_session_cookies(_):
            session = IPixelatedSession(request.getSession())
            session.user_uuid = user_auth.uuid

        language = parse_accept_language(request.getAllHeaders())
        password = request.args['password'][0]
        d = self._bootstrap_user_services.setup(user_auth, password, language)
        d.addCallback(set_session_cookies)
        d.addErrback(log_error)
