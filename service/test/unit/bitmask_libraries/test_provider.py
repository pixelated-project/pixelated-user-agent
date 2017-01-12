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
import json

from mock import patch, MagicMock, ANY
from httmock import all_requests, HTTMock, urlmatch
from requests import HTTPError
from pixelated.bitmask_libraries.provider import LeapProvider
from pixelated.bitmask_libraries.certs import LeapCertificate
from pixelated.config import leap_config
from test_abstract_leap import AbstractLeapTest
import requests


@all_requests
def not_found_mock(url, request):
    return {'status_code': 404,
            'content': 'foobar'}


@urlmatch(netloc=r'(.*\.)?some-provider\.test$', path='/provider.json')
def provider_json_mock(url, request):
    return provider_json_response("SHA256: 06e2300bdbc118c290eda0dc977c24080718f4eeca68c8b0ad431872a2baa22d")


@urlmatch(netloc=r'(.*\.)?some-provider\.test$', path='/provider.json')
def provider_json_invalid_fingerprint_mock(url, request):
    return provider_json_response("SHA256: 0123456789012345678901234567890123456789012345678901234567890123")


def provider_json_response(fingerprint):
    content = {
        "api_uri": "https://api.some-provider.test:4430",
        "api_version": "1",
        "ca_cert_fingerprint": fingerprint,
        "ca_cert_uri": "https://some-provider.test/ca.crt",
        "domain": "some-provider.test",
        "services": [
            "mx"
        ]
    }
    return {
        "status_code": 200,
        "content": json.dumps(content)
    }


@urlmatch(netloc=r'api\.some-provider\.test:4430$', path='/1/config/soledad-service.json')
def soledad_json_mock(url, request):
    content = {
        "some key": "some value",
    }
    return {
        "status_code": 200,
        "content": json.dumps(content)
    }


@urlmatch(netloc=r'api\.some-provider\.test:4430$', path='/1/config/smtp-service.json')
def smtp_json_mock(url, request):
    content = {
        "hosts": {
            "leap-mx": {
                "hostname": "mx.some-provider.test",
                "ip_address": "0.0.0.0",
                "port": 465
            }
        },
        "locations": {},
        "serial": 1,
        "version": 1
    }
    return {
        "status_code": 200,
        "content": json.dumps(content)
    }


@urlmatch(netloc=r'(.*\.)?some-provider\.test$', path='/ca.crt')
def ca_cert_mock(url, request):
    return {
        "status_code": 200,
        "content": ca_crt
    }


ca_crt = """
-----BEGIN CERTIFICATE-----
MIIFbzCCA1egAwIBAgIBATANBgkqhkiG9w0BAQ0FADBKMREwDwYDVQQKDAhXYXpv
a2F6aTEaMBgGA1UECwwRaHR0cHM6Ly9kZmkubG9jYWwxGTAXBgNVBAMMEFdhem9r
YXppIFJvb3QgQ0EwHhcNMTQwMzI1MDAwMDAwWhcNMjQwMzI1MDAwMDAwWjBKMREw
DwYDVQQKDAhXYXpva2F6aTEaMBgGA1UECwwRaHR0cHM6Ly9kZmkubG9jYWwxGTAX
BgNVBAMMEFdhem9rYXppIFJvb3QgQ0EwggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAw
ggIKAoICAQDSPyaslC6SNVsKpGoXllInPXbjiq7rJaV08Xg+64FJU/257BZZEJ/j
r33r0xlt2kj85PcbPySLKy0omXAQt9bs273hwAQXExdY41FxMD3wP/dmLqd55KYa
LDV4GUw0QPZ0QUyWVrRHkrdCDyjpRG+6GbowmtygJKLflYmUFC1PYQ3492esr0jC
+Q6L6+/D2+hBiH3NPI22Yk0kQmuPfnu2pvo+EYQ3It81qZE0Jo8u/BqOMgN2f9DS
GvSNfZcKAP18A41/VRrYFa/WUcdDxt/uP5nO1dm2vfLorje3wcMGtGRcDKG/+GAm
S0nYKKQeWYc6z5SDvPM1VlNdn1gOejhAoggT3Hr5Dq8kxW/lQZbOz+HLbz15qGjz
gL4KHKuDE6hOuqxpHdMTY4WZBBQ8/6ICBxaXH9587/nNDdZiom+XukVD4mrSMJS7
PRr14Hw57433AJDJcZRwZNRRAGgDPNsCoR2caKB6/Uwkp+dWVndj5Ad8MEjyM1yV
+fYU6PSQWNig7qqN5VhNY+zUCcez5gL6volMuW00iOkXISW4lBrcZmEAQTTcWT1D
U7EkLlwITQce63LcuvK7ZWsEm5XCqD+yUz9oQfugmIhxAlTdqt3De9FA0WT9WxGt
zLeswCNKjnMpRgTerq6elwB03EBJVc7k1QRn4+s6C30sXR12dYnEMwIDAQABo2Aw
XjAdBgNVHQ4EFgQU8ItSdI5pSqMDjgRjgYI3Nj0SwxQwDgYDVR0PAQH/BAQDAgIE
MAwGA1UdEwQFMAMBAf8wHwYDVR0jBBgwFoAU8ItSdI5pSqMDjgRjgYI3Nj0SwxQw
DQYJKoZIhvcNAQENBQADggIBALdSPUrIqyIlSMr4R7pWd6Ep0BZH5RztVUcoXtei
x2MFi/rsw7aL9qZqACYIE8Gkkh6Z6GQph0fIqhAlNFvJXKkguL3ri5xh0XmPfbv/
OLIvaUAixATivdm8ro/IqYQWdL3P6mDZOv4O6POdBEJ9JLc9RXUt1LiQ5Xb9QiLs
l/yOthhp5dJHqC8s6CDEUHRe3s9Q/4cwNB4td47I+mkLsNtVNXqi4lOzuQamqiFt
cFIqOLTFtBJ7G3k9iaDuN6RPS6LMRbqabwg4gafQTmJ+roHpnsaiHkfomI4MZOVi
TLQKOAJ3/pRGm5cGzkzQ+z4sUiCSQxtIWs7EnQCCE8agqpef6zArAvKEO+139+f2
u1BhWOm/aHT5a3INnJEbuFr8V9MlbZSxSzU3UH7hby+9PxWKYesc6KUAu6Icooci
gEQqrVhVKmfaYMLL7UZHhw56yv/6B10SSmeAMiJhtTExjjrTRLSCaKCPa2ISAUDB
aPR3t8ZoUESWRAFQGj5NvWOomTaXfyE8Or2WfNemvdlWsKvlLeVsjts+iaTgQRU9
VXcrUhrHhaXhYXeWrWkDDcl8VUlDWXzoUGV9SczOGwr6hONJWMn1HNxNV7ywFWf0
QXH1g3LBW7qNgRaGhbIX4a1WoNQDmbbKaLgKWs74atZ8o4A2aUEjomclgZWPsc5l
VeJ6
-----END CERTIFICATE-----
"""


PROVIDER_API_CERT = '/tmp/ca.crt'
PROVIDER_WEB_CERT = '/tmp/bootstrap-ca.crt'


class LeapProviderTest(AbstractLeapTest):
    def setUp(self):
        leap_config.leap_home = '/tmp/foobar'
        LeapCertificate.set_cert_and_fingerprint(PROVIDER_WEB_CERT, None)

    def tearDown(self):
        reload(leap_config)

    def test_provider_fetches_provider_json(self):
        with HTTMock(provider_json_mock, soledad_json_mock):
            provider = LeapProvider('some-provider.test')

            self.assertEqual("1", provider.api_version)
            self.assertEqual("some-provider.test", provider.domain)
            self.assertEqual("https://api.some-provider.test:4430", provider.api_uri)
            self.assertEqual("https://some-provider.test/ca.crt", provider.ca_cert_uri)
            self.assertEqual("SHA256: 06e2300bdbc118c290eda0dc977c24080718f4eeca68c8b0ad431872a2baa22d",
                             provider.ca_cert_fingerprint)
            self.assertEqual(["mx"], provider.services)

    def test_provider_json_throws_exception_on_status_code(self):
        with HTTMock(not_found_mock):
            self.assertRaises(HTTPError, LeapProvider, 'some-provider.test')

    def test_fetch_soledad_json(self):
        with HTTMock(provider_json_mock, soledad_json_mock, not_found_mock):
            provider = LeapProvider('some-provider.test')
            soledad = provider.fetch_soledad_json()

            self.assertEqual("some value", soledad.get('some key'))

    def test_fetch_smtp_json(self):
        with HTTMock(provider_json_mock, soledad_json_mock, smtp_json_mock, not_found_mock):
            provider = LeapProvider('some-provider.test')
            smtp = provider.fetch_smtp_json()
            self.assertEqual('mx.some-provider.test', smtp.get('hosts').get('leap-mx').get('hostname'))

    def test_throw_exception_for_fetch_smtp_status_code(self):
        with HTTMock(provider_json_mock, soledad_json_mock, not_found_mock):
            provider = LeapProvider('some-provider.test')
            self.assertRaises(HTTPError, provider.fetch_smtp_json)

    def test_fetch_valid_certificate(self):
        with HTTMock(provider_json_mock, soledad_json_mock, ca_cert_mock, not_found_mock):
            provider = LeapProvider('some-provider.test')
            provider.fetch_valid_certificate()

    def test_throw_exception_for_invalid_certificate(self):
        expected_exception_message = 'Certificate fingerprints don\'t match! Expected [0123456789012345678901234567890123456789012345678901234567890123] but got [06e2300bdbc118c290eda0dc977c24080718f4eeca68c8b0ad431872a2baa22d]'

        with HTTMock(provider_json_invalid_fingerprint_mock, soledad_json_mock, ca_cert_mock, not_found_mock):
            provider = LeapProvider('some-provider.test')
            with self.assertRaises(Exception) as cm:
                provider.fetch_valid_certificate()
            self.assertEqual(expected_exception_message, cm.exception.message)

    def test_that_bootstrap_cert_is_used_to_fetch_certificate(self):
        session = MagicMock(wraps=requests.session())
        session_func = MagicMock(return_value=session)
        get_func = MagicMock(wraps=requests.get)
        LeapCertificate.LEAP_CERT = PROVIDER_WEB_CERT

        with patch('pixelated.bitmask_libraries.provider.requests.session', new=session_func):
            with patch('pixelated.bitmask_libraries.provider.requests.get', new=get_func):
                with HTTMock(provider_json_mock, ca_cert_mock, soledad_json_mock, not_found_mock):
                    provider = LeapProvider('some-provider.test')
                    provider.fetch_valid_certificate()

        session.get.assert_any_call('https://some-provider.test/ca.crt', verify=PROVIDER_WEB_CERT, timeout=15)
        session.get.assert_any_call('https://some-provider.test/provider.json', verify=PROVIDER_WEB_CERT, timeout=15)

    def test_that_provider_cert_is_used_to_fetch_soledad_json(self):
        get_func = MagicMock(wraps=requests.get)

        with patch('pixelated.bitmask_libraries.provider.requests.get', new=get_func):
            with HTTMock(provider_json_mock, soledad_json_mock, not_found_mock):
                provider = LeapProvider('some-provider.test')
                provider.fetch_soledad_json()
        get_func.assert_called_with('https://api.some-provider.test:4430/1/config/soledad-service.json', verify='/tmp/foobar/providers/some-provider.test/keys/client/api.pem', timeout=15)

    def test_that_leap_fingerprint_is_validated(self):
        session = MagicMock(wraps=requests.session())
        session_func = MagicMock(return_value=session)
        LeapCertificate.set_cert_and_fingerprint(None, 'some fingerprint')

        with patch('pixelated.bitmask_libraries.provider.requests.session', new=session_func):
            with HTTMock(provider_json_mock, ca_cert_mock, soledad_json_mock, not_found_mock):
                provider = LeapProvider('some-provider.test')
                provider.fetch_valid_certificate()

        session.get.assert_any_call('https://some-provider.test/ca.crt', verify=False, timeout=15)
        session.mount.assert_called_with('https://', ANY)

    def test_provider_api_cert(self):
        with HTTMock(provider_json_mock):
            provider = LeapProvider('some-provider.test')
            certs = provider.provider_api_cert

        self.assertEqual('/tmp/foobar/providers/some-provider.test/keys/client/api.pem', certs)
