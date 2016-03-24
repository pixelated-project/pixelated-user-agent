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
import hashlib
import json
import os
from os.path import join
from string import Template
from pixelated.resources.users import UsersResource

from pixelated.resources import BaseResource, UnAuthorizedResource, UnavailableResource
from pixelated.resources import get_public_static_folder, get_protected_static_folder
from pixelated.resources import set_static_folder
from pixelated.resources.attachments_resource import AttachmentsResource
from pixelated.resources.sandbox_resource import SandboxResource
from pixelated.resources.backup_account_resource import BackupAccountResource
from pixelated.resources.contacts_resource import ContactsResource
from pixelated.resources.features_resource import FeaturesResource
from pixelated.resources.feedback_resource import FeedbackResource
from pixelated.resources.login_resource import LoginResource, LoginStatusResource
from pixelated.resources.logout_resource import LogoutResource
from pixelated.resources.user_settings_resource import UserSettingsResource
from pixelated.resources.mail_resource import MailResource
from pixelated.resources.mails_resource import MailsResource
from pixelated.resources.tags_resource import TagsResource
from pixelated.resources.keys_resource import KeysResource
from twisted.web.resource import NoResource
from twisted.web.static import File

from twisted.logger import Logger

log = Logger()


CSRF_TOKEN_LENGTH = 32

MODE_STARTUP = 1
MODE_RUNNING = 2


class RootResource(BaseResource):
    def __init__(self, services_factory, static_folder=None):
        BaseResource.__init__(self, services_factory)
        if static_folder:
            set_static_folder(static_folder)
        self._public_static_folder = get_public_static_folder()
        self._protected_static_folder = get_protected_static_folder()
        self._html_template = open(os.path.join(self._protected_static_folder, 'index.html')).read()
        self._services_factory = services_factory
        self._child_resources = ChildResourcesMap()
        with open(os.path.join(self._public_static_folder, 'interstitial.html')) as f:
            self.interstitial = f.read()
        self._startup_mode()

    def _startup_mode(self):
        self.putChild('public', File(self._public_static_folder))
        self.putChild('status', LoginStatusResource(self._services_factory))
        self._mode = MODE_STARTUP

    def getChild(self, path, request):
        if path == '':
            return self
        if self._mode == MODE_STARTUP:
            return UnavailableResource()
        if self._is_xsrf_valid(request):
            return self._child_resources.get(path)
        return UnAuthorizedResource()

    def _is_xsrf_valid(self, request):
        get_request = (request.method == 'GET')
        if get_request:
            return True

        xsrf_token = request.getCookie('XSRF-TOKEN')

        ajax_request = (request.getHeader('x-requested-with') == 'XMLHttpRequest')
        if ajax_request:
            xsrf_header = request.getHeader('x-xsrf-token')
            return xsrf_header and xsrf_header == xsrf_token

        csrf_input = request.args.get('csrftoken', [None])[0] or json.loads(request.content.read()).get('csrftoken', [None])[0]
        return csrf_input and csrf_input == xsrf_token

    def initialize(self, provider=None, disclaimer_banner=None, authenticator=None):
        self._child_resources.add('assets', File(self._protected_static_folder))
        self._child_resources.add('backup-account', BackupAccountResource(self._services_factory))
        self._child_resources.add('sandbox', SandboxResource(self._protected_static_folder))
        self._child_resources.add('keys', KeysResource(self._services_factory))
        self._child_resources.add(AttachmentsResource.BASE_URL, AttachmentsResource(self._services_factory))
        self._child_resources.add('contacts', ContactsResource(self._services_factory))
        self._child_resources.add('features', FeaturesResource(provider))
        self._child_resources.add('tags', TagsResource(self._services_factory))
        self._child_resources.add('mails', MailsResource(self._services_factory))
        self._child_resources.add('mail', MailResource(self._services_factory))
        self._child_resources.add('feedback', FeedbackResource(self._services_factory))
        self._child_resources.add('user-settings', UserSettingsResource(self._services_factory))
        self._child_resources.add('users', UsersResource(self._services_factory))
        self._child_resources.add(LoginResource.BASE_URL,
                                  LoginResource(self._services_factory, provider, disclaimer_banner=disclaimer_banner, authenticator=authenticator))
        self._child_resources.add(LogoutResource.BASE_URL, LogoutResource(self._services_factory))

        self._mode = MODE_RUNNING

    def _is_starting(self):
        return self._mode == MODE_STARTUP

    def _add_csrf_cookie(self, request):
        csrf_token = hashlib.sha256(os.urandom(CSRF_TOKEN_LENGTH)).hexdigest()
        request.addCookie('XSRF-TOKEN', csrf_token)

    def render_GET(self, request):
        self._add_csrf_cookie(request)
        if self._is_starting():
            return self.interstitial
        else:
            account_email = self.mail_service(request).account_email
            response = Template(self._html_template).safe_substitute(account_email=account_email)
            return str(response)


class ChildResourcesMap(object):
    def __init__(self):
        self._registry = {}

    def add(self, path, resource):
        self._registry[path] = resource

    def get(self, path):
        return self._registry.get(path) or NoResource()
