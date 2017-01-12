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

from twisted.internet import defer
from twisted.logger import Logger

from leap.bitmask.keymanager import KeyManager, KeyNotFound

from pixelated.config import leap_config

logger = Logger()


class UploadKeyError(Exception):
    pass


TWO_MONTHS = 60
DEFAULT_EXTENSION_THRESHOLD = TWO_MONTHS


class Keymanager(object):

    def __init__(self, provider, soledad, email_address, token, uuid):
        nicknym_url = provider._discover_nicknym_server()
        self._email = email_address
        self.keymanager = KeyManager(self._email, nicknym_url,
                                     soledad,
                                     token=token, ca_cert_path=provider.provider_api_cert, api_uri=provider.api_uri,
                                     api_version=provider.api_version,
                                     uid=uuid, gpgbinary=leap_config.gpg_binary,
                                     combined_ca_bundle=provider.combined_cerfificates_path)

    @defer.inlineCallbacks
    def generate_openpgp_key(self):
        current_key = yield self._key_exists(self._email)
        if not current_key:
            current_key = yield self._generate_key_and_send_to_leap()
        elif current_key.needs_renewal(DEFAULT_EXTENSION_THRESHOLD):
            current_key = yield self._regenerate_key_and_send_to_leap()

        self._synchronize_remote_key(current_key)
        logger.debug("Current key for {}: {}".format(self._email, current_key.fingerprint))

    @defer.inlineCallbacks
    def _synchronize_remote_key(self, current_key):
        if not self._is_key_synchronized_with_server(current_key):
            try:
                yield self.keymanager.send_key()
            except Exception as e:
                raise UploadKeyError(e.message)

    @defer.inlineCallbacks
    def _is_key_synchronized_with_server(self, current_key):
        remote_key = yield self.get_key(self._email, private=False, fetch_remote=True)
        defer.returnValue(remote_key.fingerprint == current_key.fingerprint)

    @defer.inlineCallbacks
    def _regenerate_key_and_send_to_leap(self):
        logger.info("Regenerating keys - this could take a while...")
        key = yield self.keymanager.regenerate_key()
        try:
            yield self.keymanager.send_key()
            defer.returnValue(key)
        except Exception as e:
            raise UploadKeyError(e.message)

    @defer.inlineCallbacks
    def _generate_key_and_send_to_leap(self):
        logger.info("Generating keys - this could take a while...")
        key = yield self.keymanager.gen_key()
        try:
            yield self.keymanager.send_key()
            defer.returnValue(key)
        except Exception as e:
            yield self.delete_key_pair()
            raise UploadKeyError(e.message)

    @defer.inlineCallbacks
    def _key_exists(self, email):
        try:
            current_key = yield self.get_key(email, private=True, fetch_remote=False)
            defer.returnValue(current_key)
        except KeyNotFound:
            defer.returnValue(None)

    @defer.inlineCallbacks
    def get_key(self, email, private=False, fetch_remote=True):
        key = yield self.keymanager.get_key(email, private=private, fetch_remote=fetch_remote)
        defer.returnValue(key)

    @defer.inlineCallbacks
    def delete_key_pair(self):
        private_key = yield self.get_key(self._email, private=True, fetch_remote=False)
        public_key = yield self.get_key(self._email, private=False, fetch_remote=False)

        self.keymanager.delete_key(private_key)
        self.keymanager.delete_key(public_key)
