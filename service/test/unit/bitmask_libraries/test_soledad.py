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
from mock import patch
from pixelated.bitmask_libraries.soledad import SoledadSession
from pixelated.bitmask_libraries.certs import LeapCertificate
from test_abstract_leap import AbstractLeapTest


class SoledadSessionTest(AbstractLeapTest):

    def setUp(self):
        super(SoledadSessionTest, self).setUp()

        # given
        self.provider.fetch_soledad_json.return_value = {'hosts': {
            'couch1': {
                'hostname': 'couch1.some-server.test',
                'ip_address': '192.168.1.1',
                'port': 1234
            }
        }}

    @patch('pixelated.bitmask_libraries.soledad.Soledad')
    def test_that_soledad_is_created_with_required_params(self, soledad_mock):
        soledad_mock.return_value = None
        # when
        SoledadSession(self.provider, 'any-passphrase', self.auth.token, self.auth.uuid)

        # then
        soledad_mock.assert_called_with(self.auth.uuid, passphrase=u'any-passphrase',
                                        secrets_path='%s/soledad/%s.secret' % (self.leap_home, self.auth.uuid),
                                        local_db_path='%s/soledad/%s.db' % (self.leap_home, self.auth.uuid),
                                        server_url='https://couch1.some-server.test:1234/user-%s' % self.auth.uuid,
                                        cert_file=LeapCertificate(self.provider).provider_api_cert,
                                        shared_db=None,
                                        auth_token=self.auth.token, defer_encryption=False)

    @patch('pixelated.bitmask_libraries.soledad.Soledad')
    def test_that_sync_is_called(self, soledad_mock):
        instance = soledad_mock.return_value
        instance.server_url = '/foo/bar'
        soledad_session = SoledadSession(self.provider, 'any-passphrase', self.auth.token, self.auth.uuid)

        # when
        soledad_session.sync()

        # then
        instance.sync.assert_called_with()
