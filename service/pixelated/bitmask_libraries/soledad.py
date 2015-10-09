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
import errno

import os
from twisted.internet import reactor
from leap.common.events import (
    register,
    catalog as events
)
from leap.soledad.client import Soledad
from leap.soledad.common.crypto import WrongMacError, UnknownMacMethodError
from pixelated.bitmask_libraries.certs import LeapCertificate

SOLEDAD_TIMEOUT = 120
SOLEDAD_CERT = '/tmp/ca.crt'


class SoledadDiscoverException(Exception):
    def __init__(self, *args, **kwargs):
        super(SoledadDiscoverException, self).__init__(*args, **kwargs)


class SoledadWrongPassphraseException(Exception):
    def __init__(self, *args, **kwargs):
        super(SoledadWrongPassphraseException, self).__init__(*args, **kwargs)


class SoledadSessionFactory(object):
    @classmethod
    def create(cls, provider, user_token, user_uuid, encryption_passphrase):
        return SoledadSession(provider, encryption_passphrase, user_token, user_uuid)


class SoledadSession(object):
    def __init__(self, provider, encryption_passphrase, user_token, user_uuid):
        register(events.SOLEDAD_INVALID_AUTH_TOKEN, lambda _: reactor.stop())
        self.provider = provider
        self.config = provider.config
        self.user_uuid = user_uuid
        self.user_token = user_token

        self.soledad = self._init_soledad(encryption_passphrase)

    def _init_soledad(self, encryption_passphrase):
        try:
            server_url = self._discover_soledad_server()

            self._create_database_dir()
            secrets = self._secrets_path()
            local_db = self._local_db_path()

            return Soledad(self.user_uuid,
                           passphrase=unicode(encryption_passphrase),
                           secrets_path=secrets,
                           local_db_path=local_db, server_url=server_url,
                           cert_file=LeapCertificate(self.provider).provider_api_cert,
                           shared_db=None,
                           auth_token=self.user_token,
                           defer_encryption=False)

        except (WrongMacError, UnknownMacMethodError), e:
            raise SoledadWrongPassphraseException(e)

    def _leap_path(self):
        return "%s/soledad" % self.config.leap_home

    def _secrets_path(self):
        return "%s/%s.secret" % (self._leap_path(), self.user_uuid)

    def _local_db_path(self):
        return "%s/%s.db" % (self._leap_path(), self.user_uuid)

    def _create_database_dir(self):
        try:
            os.makedirs(self._leap_path())
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(self._leap_path()):
                pass
            else:
                raise

    def sync(self):
        return self.soledad.sync()

    def _discover_soledad_server(self):
        try:
            json_data = self.provider.fetch_soledad_json()

            hosts = json_data['hosts']
            host = hosts.keys()[0]
            server_url = 'https://%s:%d/user-%s' % \
                         (hosts[host]['hostname'], hosts[host]['port'],
                          self.user_uuid)
            return server_url
        except Exception, e:
            raise SoledadDiscoverException(e)
