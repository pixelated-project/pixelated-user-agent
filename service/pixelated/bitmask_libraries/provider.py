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
import os
import fileinput
import tempfile
import requests

from leap.common.certs import get_digest
from leap.common import ca_bundle
from .certs import LeapCertificate
from pixelated.config import leap_config
from pixelated.support.tls_adapter import EnforceTLSv1Adapter

REQUESTS_TIMEOUT = 15


class LeapProvider(object):
    def __init__(self, server_name):
        self.server_name = server_name
        self.local_ca_crt = '%s/ca.crt' % leap_config.leap_home
        self.provider_json = self.fetch_provider_json()

    @property
    def provider_api_cert(self):
        return str(os.path.join(leap_config.leap_home, 'providers', self.server_name, 'keys', 'client', 'api.pem'))

    @property
    def combined_cerfificates_path(self):
        return str(os.path.join(leap_config.leap_home, 'providers', self.server_name, 'keys', 'client', 'ca_bundle'))

    @property
    def api_uri(self):
        return self.provider_json.get('api_uri')

    @property
    def ca_cert_fingerprint(self):
        return self.provider_json.get('ca_cert_fingerprint')

    @property
    def ca_cert_uri(self):
        return self.provider_json.get('ca_cert_uri')

    @property
    def api_version(self):
        return self.provider_json.get('api_version')

    @property
    def domain(self):
        return self.provider_json.get('domain')

    @property
    def services(self):
        return self.provider_json.get('services')

    def __hash__(self):
        return hash(self.server_name)

    def __eq__(self, other):
        return self.server_name == other.server_name

    def ensure_supports_mx(self):
        if 'mx' not in self.services:
            raise Exception

    def download_soledad_json(self):
        self.soledad_json = self.fetch_soledad_json()

    def download_smtp_json(self):
        self.smtp_json = self.fetch_smtp_json()

    def download_certificate(self, filename=None):
        """
        Downloads the server certificate, validates it against the provided fingerprint and stores it to file
        """
        path = filename or self.local_ca_crt

        directory = self._extract_directory(path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        cert = self.fetch_valid_certificate()
        with open(path, 'w') as out:
            out.write(cert)

    def _extract_directory(self, path):
        splited = path.split('/')
        splited.pop(-1)
        directory = '/'.join(splited)
        return directory

    def fetch_valid_certificate(self):
        cert = self._fetch_certificate()
        self.validate_certificate(cert)
        return cert

    def _fetch_certificate(self):
        cert_url = '%s/ca.crt' % self._provider_base_url()
        response = self._validated_get(cert_url)
        cert_data = response.content
        return cert_data

    def validate_certificate(self, cert_data=None):
        if cert_data is None:
            cert_data = self._fetch_certificate()

        parts = str(self.ca_cert_fingerprint).split(':')
        method = parts[0].strip()
        fingerprint = parts[1].strip()

        digest = get_digest(cert_data, method)

        if fingerprint.strip() != digest:
            raise Exception('Certificate fingerprints don\'t match! Expected [%s] but got [%s]' % (fingerprint.strip(), digest))

    def smtp_info(self):
        hosts = self.smtp_json['hosts']
        hostname = hosts.keys()[0]
        host = hosts[hostname]
        return host['hostname'], host['port']

    def _validated_get(self, url):
        session = requests.session()
        try:
            session.mount('https://', EnforceTLSv1Adapter(assert_fingerprint=LeapCertificate.LEAP_FINGERPRINT))
            response = session.get(url, verify=LeapCertificate(self).provider_web_cert, timeout=REQUESTS_TIMEOUT)
            response.raise_for_status()
            return response
        finally:
            session.close()

    def fetch_provider_json(self):
        url = '%s/provider.json' % self._provider_base_url()
        response = self._validated_get(url)
        json_data = json.loads(response.content)
        return json_data

    def fetch_soledad_json(self):
        service_url = "%s/%s/config/soledad-service.json" % (
            self.api_uri, self.api_version)
        response = requests.get(service_url, verify=self.provider_api_cert, timeout=REQUESTS_TIMEOUT)
        response.raise_for_status()
        return json.loads(response.content)

    def fetch_smtp_json(self):
        service_url = '%s/%s/config/smtp-service.json' % (
            self.api_uri, self.api_version)
        response = requests.get(service_url, verify=self.provider_api_cert, timeout=REQUESTS_TIMEOUT)
        response.raise_for_status()
        return json.loads(response.content)

    def _provider_base_url(self):
        return 'https://%s' % self.server_name

    def address_for(self, username):
        return '%s@%s' % (username, self.domain)

    def discover_soledad_server(self, user_uuid):
        hosts = self.soledad_json['hosts']
        host = hosts.keys()[0]
        server_url = 'https://%s:%d/user-%s' % \
                     (hosts[host]['hostname'], hosts[host]['port'], user_uuid)
        return server_url

    def _discover_nicknym_server(self):
        return 'https://nicknym.%s:6425/' % self.domain

    def create_combined_bundle_file(self):
        leap_ca_bundle = ca_bundle.where()

        if self.provider_api_cert == leap_ca_bundle:
            return self.provider_api_cert
        elif not self.provider_api_cert:
            return leap_ca_bundle

        with open(self.combined_cerfificates_path, 'w') as fout:
            fin = fileinput.input(files=(leap_ca_bundle, self.provider_api_cert))
            for line in fin:
                fout.write(line)
            fin.close()

    def setup_ca_bundle(self):
        path = os.path.join(leap_config.leap_home, 'providers', self.server_name, 'keys', 'client')
        if not os.path.isdir(path):
            os.makedirs(path, 0700)
        self._download_cert(self.provider_api_cert)

    def _download_cert(self, cert_file_name):
        cert = self.fetch_valid_certificate()
        with open(cert_file_name, 'w') as file:
            file.write(cert)

    def setup_ca(self):
        self.download_certificate()
        self.setup_ca_bundle()
        self.create_combined_bundle_file()

    def download_settings(self):
        self.download_soledad_json()
        self.download_smtp_json()
