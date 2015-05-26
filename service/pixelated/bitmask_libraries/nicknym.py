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
from leap.keymanager import KeyManager, openpgp
from leap.keymanager.errors import KeyNotFound
from .certs import which_api_CA_bundle
from twisted.internet import defer


class NickNym(object):
    def __init__(self, provider, config, soledad_session, username, token, uuid):
        nicknym_url = _discover_nicknym_server(provider)
        self._email = '%s@%s' % (username, provider.domain)
        self.keymanager = KeyManager('%s@%s' % (username, provider.domain), nicknym_url,
                                     soledad_session.soledad,
                                     token, which_api_CA_bundle(provider), provider.api_uri,
                                     provider.api_version,
                                     uuid, config.gpg_binary)

    @defer.inlineCallbacks
    def generate_openpgp_key(self):
        deferred = self._key_exists()
        deferred.addErrback(self._key_not_found)
        _ = yield deferred

    def _key_exists(self):
        return self.keymanager.get_key(self._email, openpgp.OpenPGPKey, private=True, fetch_remote=False)

    @defer.inlineCallbacks
    def _key_not_found(self, failure):
        failure.trap(KeyNotFound)
        deferred = self._gen_key()
        deferred.addCallback(self._send_key_to_leap)
        _ = yield deferred

    def _gen_key(self):
        print "Generating keys - this could take a while..."
        return self.keymanager.gen_key(openpgp.OpenPGPKey)

    def _send_key_to_leap(self, result):
        print "Sending key to leap"
        return self.keymanager.send_key(openpgp.OpenPGPKey)


def _discover_nicknym_server(provider):
    return 'https://nicknym.%s:6425/' % provider.domain
