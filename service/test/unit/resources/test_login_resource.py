import os

from mock import patch
from mockito import mock, when, any as ANY
from twisted.cred.error import UnauthorizedLogin
from twisted.internet import defer
from twisted.trial import unittest
from twisted.web.test.requesthelper import DummyRequest

from pixelated.resources.login_resource import LoginResource
from pixelated.resources.login_resource import parse_accept_language
from test.unit.resources import DummySite


class TestParseAcceptLanguage(unittest.TestCase):
    def test_parse_pt_br_simple(self):
        all_headers = {
            'accept-language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3'}
        parsed_language = parse_accept_language(all_headers)
        self.assertEqual('pt-BR', parsed_language)

    def test_parse_en_us_simple(self):
        all_headers = {
            'accept-language': 'en-US,en;q=0.8,en-US;q=0.5,en;q=0.3'}
        parsed_language = parse_accept_language(all_headers)
        self.assertEqual('en-US', parsed_language)

    def test_parse_pt_br_as_default(self):
        all_headers = {
            'accept-language': 'de-DE,de;q=0.8,en-US;q=0.5,en;q=0.3'}
        parsed_language = parse_accept_language(all_headers)
        self.assertEqual('pt-BR', parsed_language)


class TestLoginResource(unittest.TestCase):
    def setUp(self):
        self.services_factory = mock()
        self.portal = mock()
        self.resource = LoginResource(self.services_factory, self.portal)
        self.web = DummySite(self.resource)

    def test_children_resources_are_unauthorized_when_not_logged_in(self):
        request = DummyRequest(['/some_child_resource'])

        d = self.web.get(request)

        def assert_unauthorized_resources(_):
            self.assertEqual(401, request.responseCode)
            self.assertEqual("Unauthorized!", request.written[0])

        d.addCallback(assert_unauthorized_resources)
        return d

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

        def assert_form_rendered(_):
            self.assertEqual(200, request.responseCode)
            form_action = 'action="/login"'
            form_method = 'method="post"'
            input_username = 'name="username"'
            input_password = 'name="password"'
            input_submit = 'name="login"'
            default_disclaimer = 'Some disclaimer'
            written_response = ''.join(request.written)
            self.assertIn(form_action, written_response)
            self.assertIn(form_method, written_response)
            self.assertIn(input_password, written_response)
            self.assertIn(input_submit, written_response)
            self.assertIn(input_username, written_response)
            self.assertIn(default_disclaimer, written_response)

        d.addCallback(assert_form_rendered)
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
        self.resource = LoginResource(self.services_factory, self.provider)
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

    @patch('pixelated.authentication.Authenticator.authenticate')
    @patch('twisted.web.util.redirectTo')
    @patch('pixelated.resources.session.PixelatedSession.is_logged_in')
    def test_should_redirect_to_home_if_user_if_already_logged_in(self, mock_logged_in, mock_redirect, mock_authenticate):
        mock_logged_in.return_value = True
        when(self.services_factory).has_session(ANY()).thenReturn(True)
        mock_redirect.return_value = "mocked redirection"

        d = self.web.get(self.request)

        def assert_redirected_to_home(_):
            mock_redirect.assert_called_once_with('/', self.request)
            self.assertFalse(mock_authenticate.called)

        d.addCallback(assert_redirected_to_home)
        return d

    @patch('pixelated.config.leap.BootstrapUserServices.setup')
    @patch('pixelated.authentication.Authenticator.authenticate')
    def test_should_return_form_back_with_error_message_when_login_fails(self, mock_authenticate,
                                                                         mock_user_bootstrap_setup):
        mock_authenticate.side_effect = UnauthorizedLogin()

        d = self.web.get(self.request)

        def assert_error_response_and_user_services_not_setup(_):
            mock_authenticate.assert_called_once_with(self.username, self.password)
            self.assertEqual(401, self.request.responseCode)
            written_response = ''.join(self.request.written)
            self.assertIn('Invalid username or password', written_response)
            self.assertFalse(mock_user_bootstrap_setup.called)
            self.assertFalse(self.resource.get_session(self.request).is_logged_in())

        d.addCallback(assert_error_response_and_user_services_not_setup)
        return d

    @patch('pixelated.config.leap.BootstrapUserServices.setup')
    @patch('pixelated.authentication.Authenticator.authenticate')
    def test_successful_login_responds_interstitial(self, mock_authenticate, mock_user_bootstrap_setup):
        mock_authenticate.return_value = self.user_auth

        d = self.web.get(self.request)

        def assert_interstitial_in_response(_):
            mock_authenticate.assert_called_once_with(self.username, self.password)
            interstitial_js_in_template = '<script src="startup-assets/Interstitial.js"></script>'
            self.assertIn(interstitial_js_in_template, self.request.written[0])

        d.addCallback(assert_interstitial_in_response)
        return d

    @patch('pixelated.config.leap.BootstrapUserServices.setup')
    @patch('pixelated.authentication.Authenticator.authenticate')
    def test_successful_login_runs_user_services_bootstrap_when_interstitial_loaded(self, mock_authenticate, mock_user_bootstrap_setup):
        mock_authenticate.return_value = self.user_auth

        d = self.web.get(self.request)

        def assert_login_setup_service_for_user(_):
            mock_user_bootstrap_setup.assert_called_once_with(self.user_auth, self.password, 'pt-BR')

        d.addCallback(assert_login_setup_service_for_user)
        return d

    @patch('pixelated.config.leap.BootstrapUserServices.setup')
    @patch('pixelated.authentication.Authenticator.authenticate')
    def test_successful_adds_cookies_to_indicat_logged_in_status_when_services_are_loaded(self, mock_authenticate, mock_user_bootstrap_setup):
        mock_authenticate.return_value = self.user_auth
        irrelevant = None
        mock_user_bootstrap_setup.return_value = defer.succeed(irrelevant)

        d = self.web.get(self.request)

        def assert_login_setup_service_for_user(_):
            self.assertTrue(self.resource.get_session(self.request).is_logged_in())

        d.addCallback(assert_login_setup_service_for_user)
        return d
