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

from pixelated.config import leap_config


class LeapCertificate(object):

    LEAP_CERT = None
    LEAP_FINGERPRINT = None

    def __init__(self, provider):
        self._server_name = provider.server_name
        self._provider = provider

    @staticmethod
    def set_cert_and_fingerprint(cert_file=None, cert_fingerprint=None):
        if cert_fingerprint is None:
            LeapCertificate.LEAP_CERT = str(cert_file) if cert_file else True
            LeapCertificate.LEAP_FINGERPRINT = None
        else:
            LeapCertificate.LEAP_FINGERPRINT = cert_fingerprint
            LeapCertificate.LEAP_CERT = False

    @property
    def provider_web_cert(self):
        return self.LEAP_CERT
