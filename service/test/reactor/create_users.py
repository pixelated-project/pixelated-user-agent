#!/usr/bin/env python
# This script is used to mass register users
# ATTENTION: this script does not log
# the user in, so key creation will only
# happen on the first login
#
# You can run this with the following command:
# python create_users.py -n<number of users> -p<provider> -i<invite_code>

import argparse

import requests
from pixelated.authentication import Authenticator
from pixelated.register import register, _set_provider
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from twisted.cred.error import UnauthorizedLogin
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue, gatherResults

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class User(object):
    def __init__(self, number, provider, certificate):
        self._username = 'loadtest%d' % number
        self._password = 'password_%d' % number
        self._leap_provider = _set_provider(provider, None, certificate, None)
        self._authenticator = Authenticator(self._leap_provider)

    @inlineCallbacks
    def get_or_create_user(self, invite_code=None):
        try:
            yield self.authenticate()
        except UnauthorizedLogin:
            yield self.register(invite_code)
        user = (self._username, self._password)
        returnValue(user)

    @inlineCallbacks
    def authenticate(self):
        yield self._authenticator.authenticate(self._username, self._password)

    @inlineCallbacks
    def register(self, invite_code=None):
        yield register(self._username, self._password, self._leap_provider, invite=invite_code)


def mass_register(number, invite_code, provider):
    leap_provider = _set_provider(None, None, provider, None)
    deferreds = []
    for index in xrange(1, number + 1):
        _username = 'loadtest%d' % index
        _password = 'password_%d' % index

        def success(x, username):
            print 'done registering %s ' % username

        def failed(err, username):
            print 'ERROR registering %s: %s' % (username, err.getErrorMessage())

        d = register(_username, _password, leap_provider, invite=invite_code)
        d.addCallback(success, _username)
        d.addErrback(failed, _username)
        deferreds.append(d)
    return gatherResults(deferreds, consumeErrors=True)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--number', '-n', default=1, type=int, help='the number of user to be registered')
    parser.add_argument('--invite-code', '-i', default=None, help='invite code')
    parser.add_argument('--provider', '-p', default=None, help='leap provider e.g. unstable.pix.org')
    return parser.parse_args()


def run():
    args = _parse_args()

    def show_error(err):
        print "ERROR: %s" % err.getErrorMessage()

    def shut_down(_):
        reactor.stop()

    def _run():
        d = mass_register(args.number, args.invite_code, args.provider)
        d.addErrback(show_error)
        d.addBoth(shut_down)

    reactor.callWhenRunning(_run)
    reactor.run()

if __name__ == '__main__':
    run()
