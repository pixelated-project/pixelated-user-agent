from twisted.trial import unittest
import re

from mock import MagicMock, patch
from mockito import mock, when, any as ANY

from pixelated.application import UserAgentMode
from pixelated.resources.features_resource import FeaturesResource
from test.unit.resources import DummySite
from twisted.web.test.requesthelper import DummyRequest
from pixelated.resources.root_resource import RootResource, MODE_STARTUP, MODE_RUNNING


class TestRootResource(unittest.TestCase):
    MAIL_ADDRESS = 'test_user@pixelated-project.org'

    def setUp(self):
        self.mail_service = mock()
        self.services_factory = mock()
        self.services_factory.mode = UserAgentMode(is_single_user=True)
        self.services = mock()
        self.services.mail_service = self.mail_service
        self.services_factory._services_by_user = {'someuserid': self.mail_service}
        when(self.services_factory).services(ANY()).thenReturn(self.services)
        self.mail_service.account_email = self.MAIL_ADDRESS

        root_resource = RootResource(self.services_factory)
        root_resource._html_template = "<html><head><title>$account_email</title></head></html>"
        root_resource._mode = root_resource
        self.web = DummySite(root_resource)
        self.root_resource = root_resource

    def test_render_GET_should_template_account_email(self):
        request = DummyRequest([''])
        request.addCookie = lambda key, value: 'stubbed'

        d = self.web.get(request)

        def assert_response(_):
            expected = "<title>{0}</title>".format(self.MAIL_ADDRESS)
            matches = re.findall(expected, request.written[0])
            self.assertEquals(len(matches), 1)

        d.addCallback(assert_response)
        return d

    def _test_should_renew_xsrf_cookie(self):
        request = DummyRequest([''])
        request.addCookie = MagicMock()
        generated_csrf_token = 'csrf_token'
        mock_sha = MagicMock()
        mock_sha.hexdigest = MagicMock(return_value=generated_csrf_token)

        with patch('hashlib.sha256', return_value=mock_sha):
            d = self.web.get(request)

        def assert_csrf_cookie(_):
            request.addCookie.assert_called_once_with('XSRF-TOKEN', generated_csrf_token)

        d.addCallback(assert_csrf_cookie)
        return d

    def test_should_renew_xsrf_cookie_on_startup_mode(self):
        self.root_resource._mode = MODE_STARTUP
        self._test_should_renew_xsrf_cookie()

    def test_should_renew_xsrf_cookie_on_running_mode(self):
        self.root_resource._mode = MODE_RUNNING
        self._test_should_renew_xsrf_cookie()

    def test_should_unavailable_child_resource_during_startup(self):
        self.root_resource._mode = MODE_STARTUP

        request = DummyRequest(['/child'])
        request.getCookie = MagicMock(return_value='irrelevant -- stubbed')

        d = self.web.get(request)

        def assert_unavailable(_):
            self.assertEqual(503, request.responseCode)
            self.assertEqual("Service Unavailable", request.written[0])

        d.addCallback(assert_unavailable)
        return d

    def _mock_ajax_csrf(self, request, csrf_token):
        request.requestHeaders.setRawHeaders('x-requested-with', ['XMLHttpRequest'])
        request.requestHeaders.setRawHeaders('x-xsrf-token', [csrf_token])

    def test_should_unauthorize_child_resource_ajax_requests_when_csrf_mismatch(self):
        request = DummyRequest(['/child'])
        request.method = 'POST'
        self._mock_ajax_csrf(request, 'stubbed csrf token')

        request.getCookie = MagicMock(return_value='mismatched csrf token')

        d = self.web.get(request)

        def assert_unauthorized(_):
            self.assertEqual(401, request.responseCode)
            self.assertEqual("Unauthorized!", request.written[0])

        d.addCallback(assert_unauthorized)
        return d

    def test_should_404_non_existing_resource_with_valid_csrf(self):
        request = DummyRequest(['/non-existing-child'])
        request.method = 'POST'
        self._mock_ajax_csrf(request, 'stubbed csrf token')

        request.getCookie = MagicMock(return_value='stubbed csrf token')

        d = self.web.get(request)

        def assert_not_found(_):
            self.assertEqual(404, request.responseCode)
            self.assertIn("No Such Resource", request.written[0])

        d.addCallback(assert_not_found)
        return d

    def test_should_authorize_child_resource_non_ajax_GET_requests(self):
        request = DummyRequest(['features'])

        request.getCookie = MagicMock(return_value='irrelevant -- stubbed')
        self.root_resource._child_resources.add('features', FeaturesResource())
        self.root_resource._mode = MODE_RUNNING

        d = self.web.get(request)

        def assert_unauthorized(_):
            self.assertEqual(200, request.code)

        d.addCallback(assert_unauthorized)
        return d

    def test_should_unauthorize_child_resource_non_ajax_POST_requests_when_csrf_input_mismatch(self):
        request = DummyRequest(['mails'])
        request.method = 'POST'
        request.addArg('csrftoken', 'some csrf token')
        mock_content = MagicMock()
        mock_content.read = MagicMock(return_value={})
        request.content = mock_content

        request.getCookie = MagicMock(return_value='mismatched csrf token')

        d = self.web.get(request)

        def assert_unauthorized(_):
            self.assertEqual(401, request.responseCode)
            self.assertEqual("Unauthorized!", request.written[0])

        d.addCallback(assert_unauthorized)
        return d
