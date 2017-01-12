#
# Copyright (c) 2016 ThoughtWorks, Inc.
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
from twisted.trial import unittest
import tempdir
import leap.common.certs as certs
from mockito import mock, unstub, when, any as ANY
from pixelated.authentication import Authentication

from pixelated.config.sessions import SmtpClientCertificate

from tempfile import NamedTemporaryFile
from httmock import all_requests, HTTMock, urlmatch

CERTIFICATE_DATA = 'some cert data'
USERNAME = 'some_user_name'


@all_requests
def not_found_mock(url, request):
    return {'status_code': 404,
            'content': 'foobar'}


@urlmatch(netloc='api.some-server.test:4430', path='/1/smtp_cert', method='POST')
def smtp_cert_mock(url, request):
    if request.body == 'address=%s' % USERNAME:
        return {
            "status_code": 200,
            "content": CERTIFICATE_DATA
        }
    else:
        return {
            'status_code': 401
        }


class TestSmtpClientCertificate(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempdir.TempDir()
        self.provider = mock()
        self.provider.api_uri = 'https://api.some-server.test:4430'
        self.provider.api_version = '1'
        self.provider.server_name = 'some.host.tld'
        self.provider.domain = 'some-provider.tld'
        self.auth = Authentication(USERNAME, 'token', 'uuid', 'session_id', {})
        self.pem_path = os.path.join(self.tmp_dir.name, 'providers', 'some-provider.tld', 'keys', 'client', 'smtp.pem')

    def tearDown(self):
        self.tmp_dir.dissolve()
        unstub()

    def test_download_certificate(self):
        cert = SmtpClientCertificate(self.provider, self.auth, self.tmp_dir.name)
        when(cert).download_to(ANY()).thenReturn(None)
        result = cert.cert_path()

        self.assertEqual(self.pem_path, result)

    def test_download_certificate_if_redownload_necessary_e_g_certificate_expired(self):
        self.pretend_all_paths_exist()
        when(certs).should_redownload(self.pem_path).thenReturn(True)

        cert = SmtpClientCertificate(self.provider, self.auth, self.tmp_dir.name)
        when(cert).download_to(ANY()).thenReturn(None)
        result = cert.cert_path()

        self.assertEqual(self.pem_path, result)

    def pretend_all_paths_exist(self):
        when(os.path).exists(ANY()).thenReturn(True)

    def test_skip_download_if_already_downloaded_and_still_valid(self):
        when(os.path).exists(self.pem_path).thenReturn(True)
        when(certs).should_redownload(ANY()).thenReturn(False)
        cert = SmtpClientCertificate(self.provider, self.auth, self.tmp_dir.name)
        result = cert.cert_path()

        self.assertEqual(self.pem_path, result)

    def test_download_to(self):
        cert = SmtpClientCertificate(self.provider, self.auth, self.tmp_dir.name)

        with NamedTemporaryFile() as tmp_file:
            with HTTMock(smtp_cert_mock, not_found_mock):
                cert.download_to(tmp_file.name)

            file_content = open(tmp_file.name).read()
            self.assertEqual(CERTIFICATE_DATA, file_content)
