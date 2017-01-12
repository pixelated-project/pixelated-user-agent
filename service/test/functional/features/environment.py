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
import os
import re
import time
from urlparse import urlparse
import uuid

from crochet import setup, wait_for
from leap.common.events.server import ensure_server
from selenium import webdriver
from twisted.internet import defer

from pixelated.application import UserAgentMode
from pixelated.config.site import PixelatedSite
from pixelated.resources.features_resource import FeaturesResource
from test.support.integration import AppTestClient
from steps.common import DEFAULT_IMPLICIT_WAIT_TIMEOUT_IN_S


class UnsuportedWebDriverError(Exception):
    pass


setup()


@wait_for(timeout=5.0)
def start_app_test_client(client, mode):
    return client.start_client(mode=mode)


def before_all(context):
    _setup_webdriver(context)
    userdata = context.config.userdata
    context.host = userdata.get('host', 'http://localhost')

    if not context.host.startswith('http'):
        context.host = 'https://{}'.format(context.host)

    hostname = urlparse(context.host).hostname
    context.signup_url = 'https://{}/signup'.format(hostname)
    context.login_url = 'https://mail.{}/login'.format(hostname)
    context.username = 'testuser_{}'.format(uuid.uuid4())

    if 'localhost' in context.host:
        _mock_user_agent(context)
        context.login_url = context.multi_user_url + '/login'
        context.username = 'username'


def _setup_webdriver(context):
    browser = context.config.userdata.get('webdriver', 'phantomjs')
    supported_webdrivers = {
        'phantomjs': webdriver.PhantomJS,
        'firefox': webdriver.Firefox,
        'chrome': webdriver.Chrome,
    }

    try:
        context.browser = supported_webdrivers[browser]()
    except KeyError:
        raise UnsuportedWebDriverError('{} is not a supported webdriver'.format(browser))

    context.browser.set_window_size(1280, 1024)
    context.browser.implicitly_wait(DEFAULT_IMPLICIT_WAIT_TIMEOUT_IN_S)
    context.browser.set_page_load_timeout(60)


def _mock_user_agent(context):
    ensure_server()
    PixelatedSite.disable_csp_requests()
    FeaturesResource.DISABLED_FEATURES.append('autoRefresh')

    context.single_user_url = _define_url(8889)
    context.single_user_client = _start_user_agent(8889, is_single_user=True)

    context.multi_user_url = _define_url(4568)
    context.multi_user_client = _start_user_agent(4568, is_single_user=False)


def _start_user_agent(port, is_single_user):
    client = AppTestClient()
    start_app_test_client(client, UserAgentMode(is_single_user=is_single_user))
    client.listenTCP(port=port)
    return client


def _define_url(port):
    return 'http://localhost:{port}'.format(port=port)


def after_all(context):
    context.browser.quit()
    if 'localhost' in context.host:
        context.single_user_client.stop()


def before_feature(context, feature):
    if 'localhost' in context.host:
        context.browser.get(context.single_user_url)


def after_feature(context, feature):
    if 'localhost' in context.host:
        cleanup_all_mails(context)
        context.last_mail = None


def after_step(context, step):
    _debug_on_error(context, step)
    _save_screenshot(context, step)


def _debug_on_error(context, step):
    if step.status == 'failed' and context.config.userdata.getbool("debug"):
        try:
            import ipdb
            ipdb.post_mortem(step.exc_traceback)
        except ImportError:
            import pdb
            pdb.post_mortem(step.exc_traceback)


def _save_screenshot(context, step):
    if (step.status == 'failed' and
            context.config.userdata.getbool("screenshots", True)):
        timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
        filename = _slugify('{} failed {}'.format(timestamp, str(step.name)))
        filepath = os.path.join('screenshots', filename + '.png')
        context.browser.save_screenshot(filepath)


def _slugify(string_):
    return re.sub('\W', '-', string_)


@wait_for(timeout=10.0)
def cleanup_all_mails(context):
    @defer.inlineCallbacks
    def _delete_all_mails():
        mails = yield context.single_user_client.mail_store.all_mails()
        for mail in mails:
            yield context.single_user_client.mail_store.delete_mail(mail.ident)

    return _delete_all_mails()
