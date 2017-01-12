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
import re
from collections import namedtuple

from leap.bitmask.bonafide.provider import Api
from leap.bitmask.bonafide.session import Session
from leap.bitmask.bonafide._srp import SRPAuthError

from twisted.cred.error import UnauthorizedLogin
from twisted.internet.defer import inlineCallbacks, returnValue

Credentials = namedtuple('Credentials', 'username, password')


class Authenticator(object):
    def __init__(self, leap_provider):
        self._leap_provider = leap_provider
        self.domain = leap_provider.server_name

    @inlineCallbacks
    def authenticate(self, username, password):
        username = self.clean_username(username)
        auth = yield self._srp_auth(username, password)
        returnValue(auth)

    @inlineCallbacks
    def _srp_auth(self, username, password):
        try:
            auth = yield self._bonafide_auth(username, password)
        except SRPAuthError:
            raise UnauthorizedLogin("User typed wrong password/username combination.")
        returnValue(auth)

    @inlineCallbacks
    def _bonafide_auth(self, user, password):
        srp_provider = Api(self._leap_provider.api_uri)
        credentials = Credentials(user, password)
        srp_auth = Session(credentials, srp_provider, self._leap_provider.local_ca_crt)
        yield srp_auth.authenticate()
        returnValue(Authentication(user, srp_auth.token, srp_auth.uuid, 'session_id', {'is_admin': False}))

    def clean_username(self, username):
        if '@' not in username:
            return username
        extracted_username = self.extract_username(username)
        if self.username_with_domain(extracted_username) == username:
            return extracted_username
        raise UnauthorizedLogin('User typed a wrong domain.')

    def extract_username(self, username):
        return re.search('^([^@]+)@?.*$', username).group(1)

    def username_with_domain(self, username):
        return '%s@%s' % (username, self.domain)


class Authentication(object):
    def __init__(self, username, token, uuid, session_id, user_attributes):
        self.username = username
        self.token = token
        self.uuid = uuid
        self.session_id = session_id
        self._user_attributes = user_attributes

    def is_admin(self):
        return self._user_attributes.get('is_admin', False)
