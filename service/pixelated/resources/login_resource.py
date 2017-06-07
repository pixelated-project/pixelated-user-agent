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

from pixelated.config.leap import BootstrapUserServices
from pixelated.resources import BaseResource, UnAuthorizedResource, IPixelatedSession
from pixelated.resources.account_recovery_resource import AccountRecoveryResource
from pixelated.resources import get_public_static_folder, respond_json
from pixelated.support.language import parse_accept_language

from twisted.cred.error import UnauthorizedLogin
from twisted.internet import defer
from twisted.logger import Logger
from twisted.python.filepath import FilePath
from twisted.web import util
from twisted.web.http import OK
from twisted.web.resource import NoResource
from twisted.web.server import NOT_DONE_YET
from twisted.web.static import File
from twisted.web.template import Element, XMLFile, renderElement, renderer

log = Logger()


class DisclaimerElement(Element):
    loader = XMLFile(FilePath(os.path.join(get_public_static_folder(), '_login_disclaimer_banner.html')))

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
    loader = XMLFile(FilePath(os.path.join(get_public_static_folder(), 'login.html')))

    def __init__(self, disclaimer_banner_file=None):
        super(LoginWebSite, self).__init__()
        self.disclaimer_banner_file = disclaimer_banner_file

    @renderer
    def disclaimer(self, request, tag):
        return DisclaimerElement(self.disclaimer_banner_file).render(request)


class LoginResource(BaseResource):
    BASE_URL = 'login'

    def __init__(self, services_factory, provider=None, disclaimer_banner=None, authenticator=None):
        BaseResource.__init__(self, services_factory)
        self._disclaimer_banner = disclaimer_banner
        self._provider = provider
        self._authenticator = authenticator
        self._bootstrap_user_services = BootstrapUserServices(services_factory, provider)

        static_folder = get_public_static_folder()
        self.putChild('public', File(static_folder))
        with open(os.path.join(static_folder, 'interstitial.html')) as f:
            self.interstitial = f.read()

    def getChild(self, path, request):
        if path == '':
            return self
        if path == 'login':
            return self
        if path == 'status':
            return LoginStatusResource(self._services_factory)
        if path == AccountRecoveryResource.BASE_URL:
            return AccountRecoveryResource(self._services_factory, self._provider)
        if not self.is_logged_in(request):
            return UnAuthorizedResource()
        return NoResource()

    def render_GET(self, request):
        request.setResponseCode(OK)
        return self._render_template(request)

    def _render_template(self, request):
        site = LoginWebSite(disclaimer_banner_file=self._disclaimer_banner)
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
            if error.type is UnauthorizedLogin:
                log.info('Unauthorized login for %s. %s' % (request.args['username'][0], error.getErrorMessage()))
                content = util.redirectTo("/login?auth-error", request)
            else:
                log.error('Authentication error for %s: %s \n %s' % (request.args['username'][0], error.getErrorMessage(), error.getTraceback()))
                content = util.redirectTo("/login?error", request)

            request.write(content)
            request.finish()

        d = self._handle_login(request)
        d.addCallbacks(render_response, render_error)
        return NOT_DONE_YET

    @defer.inlineCallbacks
    def _handle_login(self, request):
        username = request.args['username'][0]
        password = request.args['password'][0]
        user_auth = yield self._authenticator.authenticate(username, password)
        defer.returnValue(user_auth)

    def _complete_bootstrap(self, user_auth, request):
        def login_error(error, session):
            log.error('Login error during %s services setup: %s \n %s' % (user_auth.username, error.getErrorMessage(), error.getTraceback()))
            session.login_error()

        def login_successful(_, session):
            session.login_successful(user_auth.uuid)

        language = parse_accept_language(request.getAllHeaders())
        password = request.args['password'][0]
        session = IPixelatedSession(request.getSession())
        session.login_started()

        d = self._bootstrap_user_services.setup(user_auth, password, language)
        d.addCallback(login_successful, session)
        d.addErrback(login_error, session)


class LoginStatusResource(BaseResource):
    isLeaf = True

    def __init__(self, services_factory):
        BaseResource.__init__(self, services_factory)

    def render_GET(self, request):
        session = IPixelatedSession(request.getSession())
        status = 'completed' if self._services_factory.mode.is_single_user else str(session.check_login_status())

        response = {'status': status}
        return respond_json(response, request)
