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

import os

from mock import patch, MagicMock
from mockito import mock, when, any as ANY
from twisted.cred.error import UnauthorizedLogin
from twisted.internet import defer
from twisted.trial import unittest
from twisted.web.test.requesthelper import DummyRequest

from pixelated.resources.login_resource import LoginResource, LoginStatusResource
from test.unit.resources import DummySite


class TestLoginResource(unittest.TestCase):
    def setUp(self):
        self.services_factory = mock()
        self.portal = mock()
        self.resource = LoginResource(self.services_factory, self.portal, authenticator=mock())
        self.web = DummySite(self.resource)

    def test_children_resources_are_unauthorized_when_not_logged_in(self):
        request = DummyRequest(['/some_child_resource'])

        d = self.web.get(request)

        def assert_unauthorized_resources(_):
            self.assertEqual(401, request.responseCode)
            self.assertEqual("Unauthorized!", request.written[0])

        d.addCallback(assert_unauthorized_resources)
        return d

    def test_account_recovery_resource_does_not_require_login(self):
        request = DummyRequest(['account-recovery'])
        d = self.web.get(request)

        def assert_successful(_):
            self.assertEqual(200, request.responseCode)

        d.addCallback(assert_successful)
        return d

    def test_get_child_for_account_recovery_path(self):
        request = DummyRequest(['account-recovery'])
        result = self.resource.getChild('account-recovery', request)
        self.assertEqual(result._authenticator._leap_provider, self.portal)

    @patch('pixelated.resources.session.PixelatedSession.is_logged_in')
    def test_there_are_no_grand_children_resources_when_logged_in(self, mock_is_logged_in):
        request = DummyRequest(['/login/grand_children'])
        mock_is_logged_in.return_value = True
        when(self.services_factory).has_session(ANY()).thenReturn(True)

        d = self.web.get(request)

        def assert_resources_not_found(_):
            self.assertEqual(404, request.responseCode)
            self.assertIn("No Such Resource", request.written[0])

        d.addCallback(assert_resources_not_found)
        return d

    def test_get(self):
        request = DummyRequest([''])

        d = self.web.get(request)

        def assert_login_page_rendered(_):
            self.assertEqual(200, request.responseCode)
            title = 'Pixelated - Login'
            default_disclaimer = 'Some disclaimer'
            written_response = ''.join(request.written)
            self.assertIn(title, written_response)
            self.assertIn(default_disclaimer, written_response)

        d.addCallback(assert_login_page_rendered)
        return d

    def _write(self, filename, content):
        with open(filename, 'w') as disclaimer_file:
            disclaimer_file.write(content)

    def test_override_login_disclaimer_message(self):
        request = DummyRequest([''])

        banner_file_name = 'banner.txt'
        banner_disclaimer_content = '<p>some custom disclaimer</p>'
        self._write(banner_file_name, banner_disclaimer_content)

        self.resource._disclaimer_banner = 'service/_trial_temp/' + banner_file_name

        d = self.web.get(request)

        def assert_custom_disclaimer_rendered(_):
            self.assertEqual(200, request.responseCode)
            written_response = ''.join(request.written)
            self.assertIn(banner_disclaimer_content, written_response)

        def tear_down(_):
            os.remove(banner_file_name)

        d.addCallback(assert_custom_disclaimer_rendered)
        d.addCallback(tear_down)
        return d

    def test_non_xml_compliant_banner_will_send_default_invalid_format_banner(self):
        request = DummyRequest([''])

        banner_file_name = 'banner.txt'
        xml_invalid_banner = '<p>some unclosed paragraph'
        self._write(banner_file_name, xml_invalid_banner)

        self.resource._disclaimer_banner = 'service/_trial_temp/' + banner_file_name

        d = self.web.get(request)

        def assert_default_invalid_banner_disclaimer_rendered(_):
            self.assertEqual(200, request.responseCode)
            written_response = ''.join(request.written)
            self.assertIn("Invalid XML template format for service/_trial_temp/banner.txt.", written_response)

        def tear_down(_):
            os.remove(banner_file_name)

        d.addCallback(assert_default_invalid_banner_disclaimer_rendered)
        d.addCallback(tear_down)
        return d

    def test_wrong_banner_file_location_will_send_default_invalid_format_banner(self):
        request = DummyRequest([''])

        non_existing_banner_file = 'banner.txt'

        self.resource._disclaimer_banner = non_existing_banner_file

        d = self.web.get(request)

        def assert_default_invalid_banner_disclaimer_rendered(_):
            self.assertEqual(200, request.responseCode)
            written_response = ''.join(request.written)
            self.assertIn("Disclaimer banner file banner.txt could not be read or does not exit.", written_response)

        d.addCallback(assert_default_invalid_banner_disclaimer_rendered)
        return d


class TestLoginPOST(unittest.TestCase):
    def setUp(self):
        self.services_factory = mock()
        self.provider = mock()
        self.authenticator = MagicMock()
        self.resource = LoginResource(self.services_factory, self.provider, authenticator=self.authenticator)
        self.web = DummySite(self.resource)

        self.request = DummyRequest([''])
        username = 'ayoyo'
        self.request.addArg('username', username)
        password = 'ayoyo_password'
        self.username = username
        self.password = password
        self.request.addArg('password', password)
        self.request.method = 'POST'
        user_auth = mock()
        user_auth.uuid = 'some_user_uuid'
        self.user_auth = user_auth

    @patch('twisted.web.util.redirectTo')
    @patch('pixelated.resources.session.PixelatedSession.is_logged_in')
    def test_should_redirect_to_home_if_user_if_already_logged_in(self, mock_logged_in, mock_redirect):
        mock_logged_in.return_value = True
        when(self.services_factory).has_session(ANY()).thenReturn(True)
        mock_redirect.return_value = "mocked redirection"

        d = self.web.get(self.request)

        def assert_redirected_to_home(_):
            mock_redirect.assert_called_once_with('/', self.request)
            self.assertFalse(self.authenticator.authenticate.called)

        d.addCallback(assert_redirected_to_home)
        return d

    @patch('pixelated.config.leap.BootstrapUserServices.setup')
    @patch('twisted.web.util.redirectTo')
    def test_should_redirect_to_login_with_error_flag_when_login_fails(self,
                                                                       mock_redirect,
                                                                       mock_user_bootstrap_setup):
        self.authenticator.authenticate.side_effect = UnauthorizedLogin()
        mock_redirect.return_value = "mocked redirection"

        d = self.web.get(self.request)

        def assert_redirected_to_login(_):
            self.authenticator.authenticate.assert_called_once_with(self.username, self.password)
            mock_redirect.assert_called_once_with('/login?auth-error', self.request)
            self.assertFalse(mock_user_bootstrap_setup.called)
            self.assertFalse(self.resource.get_session(self.request).is_logged_in())

        d.addCallback(assert_redirected_to_login)
        return d

    @patch('pixelated.config.leap.BootstrapUserServices.setup')
    def test_successful_login_responds_interstitial(self, mock_user_bootstrap_setup):
        self.authenticator.authenticate.return_value = self.user_auth

        d = self.web.get(self.request)

        def assert_interstitial_in_response(_):
            self.authenticator.authenticate.assert_called_once_with(self.username, self.password)
            interstitial_js_in_template = '<script src="/public/interstitial.js"></script>'
            self.assertIn(interstitial_js_in_template, self.request.written[0])

        d.addCallback(assert_interstitial_in_response)
        return d

    @patch('pixelated.config.leap.BootstrapUserServices.setup')
    def test_successful_login_runs_user_services_bootstrap_when_interstitial_loaded(self, mock_user_bootstrap_setup):
        self.authenticator.authenticate.return_value = self.user_auth

        d = self.web.get(self.request)

        def assert_login_setup_service_for_user(_):
            mock_user_bootstrap_setup.assert_called_once_with(self.user_auth, self.password, 'en-US')

        d.addCallback(assert_login_setup_service_for_user)
        return d

    @patch('pixelated.config.leap.BootstrapUserServices.setup')
    def test_successful_adds_cookies_to_indicate_logged_in_status_when_services_are_loaded(self, mock_user_bootstrap_setup):
        self.authenticator.authenticate.return_value = self.user_auth
        irrelevant = None
        mock_user_bootstrap_setup.return_value = defer.succeed(irrelevant)

        d = self.web.get(self.request)

        def assert_login_setup_service_for_user(_):
            self.assertTrue(self.resource.get_session(self.request).is_logged_in())

        d.addCallback(assert_login_setup_service_for_user)
        return d

    @patch('pixelated.resources.session.PixelatedSession.login_started')
    def test_session_adds_login_started_status_after_authentication(self, mock_login_started):
        self.authenticator.authenticate.return_value = self.user_auth

        d = self.web.get(self.request)

        def assert_login_started_called(_):
            mock_login_started.assert_called_once()

        d.addCallback(assert_login_started_called)
        return d

    @patch('pixelated.resources.session.PixelatedSession.login_successful')
    @patch('pixelated.config.leap.BootstrapUserServices.setup')
    def test_session_adds_login_successful_status_when_services_setup_finishes(self, mock_user_bootstrap_setup, mock_login_successful):
        self.authenticator.authenticate.return_value = self.user_auth
        mock_user_bootstrap_setup.return_value = defer.succeed(None)

        d = self.web.get(self.request)

        def assert_login_successful_called(_):
            mock_login_successful.assert_called_once()

        d.addCallback(assert_login_successful_called)
        return d

    @patch('pixelated.resources.session.PixelatedSession.login_error')
    @patch('pixelated.config.leap.BootstrapUserServices.setup')
    def test_session_adds_login_error_status_when_services_setup_gets_error(self, mock_user_bootstrap_setup, mock_login_error):
        self.authenticator.authenticate.return_value = self.user_auth
        mock_user_bootstrap_setup.return_value = defer.fail(Exception('Could not setup user services'))

        d = self.web.get(self.request)

        def assert_login_error_called(_):
            mock_login_error.assert_called_once()

        d.addCallback(assert_login_error_called)
        return d


class TestLoginStatus(unittest.TestCase):
    def setUp(self):
        self.services_factory = mock()
        self.resource = LoginStatusResource(self.services_factory)
        self.web = DummySite(self.resource)

        self.request = DummyRequest(['/status'])

    def test_login_status_completed_when_single_user(self):
        self.services_factory.mode = mock()
        self.services_factory.mode.is_single_user = True
        d = self.web.get(self.request)

        def assert_login_completed(_):
            self.assertIn('completed', self.request.written[0])

        d.addCallback(assert_login_completed)
        return d

    @patch('pixelated.resources.session.PixelatedSession.check_login_status')
    def test_login_status_when_multi_user_returns_check_login_status(self, mock_login_status):
        self.services_factory.mode = mock()
        self.services_factory.mode.is_single_user = False
        mock_login_status.return_value = 'started'
        d = self.web.get(self.request)

        def assert_login_completed(_):
            self.assertIn('started', self.request.written[0])

        d.addCallback(assert_login_completed)
        return d
