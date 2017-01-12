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
import getpass
import re
from collections import namedtuple

from leap.bitmask.bonafide.provider import Api
from leap.bitmask.bonafide.session import Session
from pixelated.bitmask_libraries.certs import LeapCertificate
from pixelated.bitmask_libraries.provider import LeapProvider
from pixelated.config import arguments
from pixelated.config import leap_config
from pixelated.config import logger as logger_config
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.logger import Logger

Credentials = namedtuple('Credentials', 'username, password')

logger = Logger()


def _validate(username, password):
    validate_username(username)
    validate_password(password)


def _set_provider(provider_cert, provider_cert_fingerprint, server_name, leap_home=None):
    if leap_home:
        leap_config.set_leap_home(leap_home)

    LeapCertificate.set_cert_and_fingerprint(provider_cert, provider_cert_fingerprint)
    provider = LeapProvider(server_name)
    provider.setup_ca()
    provider.download_settings()
    return provider


def _set_leap_provider(args):
    return _set_provider(args.leap_provider_cert, args.leap_provider_cert_fingerprint, args.provider, args.leap_home)


def _bonafide_session(username, password, provider):
    srp_provider = Api(provider.api_uri)
    credentials = Credentials(username, password)
    return Session(credentials, srp_provider, provider.local_ca_crt)


def log_results(created, username):
    if created:
        logger.info('User %s successfully registered' % username)
    else:
        logger.error("Register failed")


@inlineCallbacks
def register(username, password, leap_provider, invite=None):
    if not password:
        password = getpass.getpass('Please enter password for %s: ' % username)

    _validate(username, password)
    logger.info('password validated...')
    srp_auth = _bonafide_session(username, password, leap_provider)

    created, user = yield srp_auth.signup(username, password, invite)
    log_results(created, username)


def validate_username(username):
    accepted_characters = '^[a-z0-9\-\_\.]*$'
    if not re.match(accepted_characters, username):
        raise ValueError('Only lowercase letters, digits, . - and _ allowed.')


def validate_password(password):
    if len(password) < 8:
        logger.info('password not validated...')
        raise ValueError('The password must have at least 8 characters')


def initialize():
    logger_config.init(debug=False)
    args = arguments.parse_register_args()
    leap_provider = _set_leap_provider(args)

    def show_error(err):
        logger.info('error: %s' % err)

    def shut_down(_):
        reactor.stop()

    def _register():
        d = register(
            args.username,
            args.password,
            leap_provider,
            args.invite_code)
        d.addErrback(show_error)
        d.addBoth(shut_down)

    reactor.callWhenRunning(_register)
    reactor.run()
