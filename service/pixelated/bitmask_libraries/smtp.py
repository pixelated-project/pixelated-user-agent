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
import logging
import os
import requests
from .certs import which_api_CA_bundle
from leap.mail.smtp import setup_smtp_gateway


logger = logging.getLogger(__name__)


class LeapSmtp(object):

    TWISTED_PORT = 4650

    def __init__(self, provider, username, session_id, keymanager=None):
        self._provider = provider
        self.username = username
        self.session_id = session_id
        self._keymanager = keymanager
        self._hostname, self._port = self._discover_smtp_server()
        self._smtp_port = None
        self._smtp_service = None

    def smtp_info(self):
        return ('localhost', self.TWISTED_PORT)

    def _discover_smtp_server(self):
        json_data = self._provider.fetch_smtp_json()
        hosts = json_data['hosts']
        hostname = hosts.keys()[0]
        host = hosts[hostname]

        hostname = host['hostname']
        port = host['port']

        return hostname, port

    def _download_client_certificates(self):
        cert_path = self._client_cert_path()

        if not os.path.exists(os.path.dirname(cert_path)):
            os.makedirs(os.path.dirname(cert_path))

        cert_url = '%s/%s/cert' % (self._provider.api_uri, self._provider.api_version)
        cookies = {"_session_id": self.session_id}

        response = requests.get(cert_url, verify=which_api_CA_bundle(self._provider), cookies=cookies, timeout=self._provider.config.timeout_in_s)
        response.raise_for_status()

        client_cert = response.content

        with open(cert_path, 'w') as f:
            f.write(client_cert)

    def _client_cert_path(self):
        return os.path.join(
            self._provider.config.leap_home,
            "providers",
            self._provider.domain,
            "keys", "client", "smtp.pem")

    def start(self):
        self._download_client_certificates()
        cert_path = self._client_cert_path()
        email = '%s@%s' % (self.username, self._provider.domain)

        self._smtp_service, self._smtp_port = setup_smtp_gateway(
            port=self.TWISTED_PORT,
            userid=str(email),
            keymanager=self._keymanager,
            smtp_host=self._hostname.encode('UTF-8'),
            smtp_port=self._port,
            smtp_cert=cert_path,
            smtp_key=cert_path,
            encrypted_only=False
        )

    def ensure_running(self):
        if not self._smtp_service:
            try:
                self.start()
            except:
                logger.warning("Couldn't start the SMTP server now, will try again when the user tries to use it")
                return False
        return True

    def stop(self):
        if self._smtp_service is not None:
            self._smtp_port.stopListening()
            self._smtp_service.doStop()
            self._smtp_port = None
            self._smtp_service = None
