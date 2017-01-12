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

import re

from pixelated.resources import IPixelatedSession
from twisted.cred import error
from twisted.cred import portal, checkers
from twisted.cred.checkers import ANONYMOUS
from twisted.cred.credentials import ICredentials
from twisted.internet import defer
from twisted.logger import Logger
from twisted.web import util
from twisted.web._auth.wrapper import UnauthorizedResource
from twisted.web.error import UnsupportedMethod
from twisted.web.resource import IResource, ErrorPage
from zope.interface import implements, implementer, Attribute


log = Logger()


class ISessionCredential(ICredentials):

    request = Attribute('the current request')


@implementer(ISessionCredential)
class SessionCredential(object):
    def __init__(self, request):
        self.request = request


@implementer(checkers.ICredentialsChecker)
class SessionChecker(object):
    credentialInterfaces = (ISessionCredential,)

    def __init__(self, services_factory):
        self._services_factory = services_factory

    def requestAvatarId(self, credentials):
        session = self.get_session(credentials.request)
        if session.is_logged_in() and self._services_factory.has_session(session.user_uuid):
            return defer.succeed(session.user_uuid)
        return defer.succeed(ANONYMOUS)

    def get_session(self, request):
        return IPixelatedSession(request.getSession())


class PixelatedRealm(object):
    implements(portal.IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        if IResource in interfaces:
            return IResource, avatarId, lambda: None
        raise NotImplementedError()


@implementer(IResource)
class PixelatedAuthSessionWrapper(object):

    isLeaf = False

    def __init__(self, portal, root_resource, anonymous_resource, credentialFactories):
        self._portal = portal
        self._credentialFactories = credentialFactories
        self._root_resource = root_resource
        self._anonymous_resource = anonymous_resource

    def render(self, request):
        raise UnsupportedMethod(())

    def getChildWithDefault(self, path, request):
        request.postpath.insert(0, request.prepath.pop())
        return self._authorizedResource(request)

    def _authorizedResource(self, request):
        creds = SessionCredential(request)
        return util.DeferredResource(self._login(creds, request))

    def _login(self, credentials, request):
        pattern = re.compile("^/sandbox/")

        def loginSucceeded(args):
            interface, avatar, logout = args
            if avatar == checkers.ANONYMOUS and not pattern.match(request.path):
                return self._anonymous_resource
            else:
                return self._root_resource

        def loginFailed(result):
            if result.check(error.Unauthorized, error.LoginFailed):
                return UnauthorizedResource(self._credentialFactories)
            else:
                log.err(
                    result,
                    "HTTPAuthSessionWrapper.getChildWithDefault encountered "
                    "unexpected error")
                return ErrorPage(500, None, None)

        d = self._portal.login(credentials, None, IResource)
        d.addCallbacks(loginSucceeded, loginFailed)
        return d
