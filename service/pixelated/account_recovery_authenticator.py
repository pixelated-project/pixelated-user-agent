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

from twisted.cred.error import UnauthorizedLogin

from authentication import Authenticator


class AccountRecoveryAuthenticator(Authenticator):
    def __init__(self, leap_provider):
        super(AccountRecoveryAuthenticator, self).__init__(leap_provider, recovery_session=True)

    def _auth_error(self):
        raise UnauthorizedLogin("User typed wrong username/recovery-code combination.")
