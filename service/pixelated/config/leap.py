#
# Copyright (c) 2015 ThoughtWorks, Inc.
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

from __future__ import absolute_import

from leap.common.events import (server as events_server)
from pixelated.adapter.welcome_mail import add_welcome_mail
from pixelated.authentication import Authenticator
from pixelated.bitmask_libraries.certs import LeapCertificate
from pixelated.bitmask_libraries.provider import LeapProvider
from pixelated.config import credentials
from pixelated.config import leap_config
from pixelated.config.sessions import LeapSessionFactory
from twisted.internet import defer
from twisted.logger import Logger

log = Logger()


def initialize_leap_provider(provider_hostname, provider_cert, provider_fingerprint, leap_home):
    LeapCertificate.set_cert_and_fingerprint(provider_cert,
                                             provider_fingerprint)
    leap_config.set_leap_home(leap_home)
    provider = LeapProvider(provider_hostname)
    provider.setup_ca()
    provider.download_settings()
    return provider


@defer.inlineCallbacks
def initialize_leap_multi_user(provider_hostname,
                               leap_provider_cert,
                               leap_provider_cert_fingerprint,
                               credentials_file,
                               leap_home):

    config, provider = initialize_leap_provider(provider_hostname, leap_provider_cert, leap_provider_cert_fingerprint, leap_home)

    defer.returnValue((config, provider))


@defer.inlineCallbacks
def create_leap_session(provider, username, password, auth=None):
    leap_session = yield LeapSessionFactory(provider).create(username, password, auth)
    defer.returnValue(leap_session)


@defer.inlineCallbacks
def initialize_leap_single_user(leap_provider_cert,
                                leap_provider_cert_fingerprint,
                                credentials_file,
                                leap_home):

    init_monkeypatches()
    events_server.ensure_server()

    provider, username, password = credentials.read(credentials_file)

    provider = initialize_leap_provider(provider, leap_provider_cert, leap_provider_cert_fingerprint, leap_home)

    auth = yield Authenticator(provider).authenticate(username, password)

    leap_session = yield create_leap_session(provider, username, password, auth)

    defer.returnValue(leap_session)


def init_monkeypatches():
    import pixelated.extensions.requests_urllib3


class BootstrapUserServices(object):

    def __init__(self, services_factory, provider):
        self._services_factory = services_factory
        self._provider = provider

    @defer.inlineCallbacks
    def setup(self, user_auth, password, language='pt-BR'):
        leap_session = None
        try:
            leap_session = yield create_leap_session(self._provider, user_auth.username, password, user_auth)
            yield self._setup_user_services(leap_session)
            yield self._add_welcome_email(leap_session, language)
        except Exception as e:
            log.warn('{0}: {1}. Closing session for user: {2}'.format(e.__class__.__name__, e, user_auth.username))
            if leap_session:
                leap_session.close()
            raise e

    @defer.inlineCallbacks
    def _setup_user_services(self, leap_session):
        user_id = leap_session.user_auth.uuid
        if not self._services_factory.has_session(user_id):
            yield self._services_factory.create_services_from(leap_session)
            self._services_factory.map_email(leap_session.user_auth.username, user_id)

    @defer.inlineCallbacks
    def _add_welcome_email(self, leap_session, language):
        if leap_session.fresh_account:
            yield add_welcome_mail(leap_session.mail_store, language)
