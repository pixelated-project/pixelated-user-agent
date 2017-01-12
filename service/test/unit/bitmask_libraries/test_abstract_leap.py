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
import tempfile
from twisted.trial import unittest
from uuid import uuid4

import os
from mock import Mock, MagicMock
from pixelated.adapter.mailstore import MailStore


class AbstractLeapTest(unittest.TestCase):

    def setUp(self):
        self._uuid = str(uuid4())
        self._token = str(uuid4())

        self.leap_home = os.path.join(tempfile.mkdtemp(), 'leap')

        self.config = Mock(leap_home=self.leap_home, bootstrap_ca_cert_bundle='/some/path/to/ca_cert', ca_cert_bundle='/some/path/to/provider_ca_cert', gpg_binary='/path/to/gpg')
        self.provider = Mock(config=self.config, server_name='some-server.test', domain='some-server.test',
                             api_uri='https://api.some-server.test:4430', api_version='1')
        self.soledad = Mock()
        self.soledad_session = Mock(soledad=self.soledad)
        self.auth = Mock(username='test_user',
                         api_server_name='some-server.test',
                         uuid=self._uuid,
                         token=self._token)

        self.keymanager = MagicMock()

        self.soledad_account = MagicMock()

        self.mail_fetcher_mock = MagicMock()

        self.mail_store = MagicMock(spec=MailStore)
