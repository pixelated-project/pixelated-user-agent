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

from mock import patch, MagicMock
from mockito import when
from unittest import TestCase
from pixelated.bitmask_libraries.keymanager import Keymanager
from pixelated.bitmask_libraries.keymanager import UploadKeyError
from pixelated.config import leap_config
from twisted.internet import defer


class KeymanagerTest(TestCase):

    def setUp(self):
        self.provider = MagicMock()
        self.soledad = MagicMock()
        self.auth = MagicMock(token='token', auth='auth')
        self.leap_keymanager = MagicMock()
        with patch('pixelated.bitmask_libraries.keymanager.KeyManager', return_value=self.leap_keymanager):
            self.keymanager = Keymanager(self.provider,
                                         self.soledad,
                                         'test_user@some-server.test',
                                         self.auth.token,
                                         self.auth.uuid)

    def tearDown(self):
        reload(leap_config)

    @patch('pixelated.bitmask_libraries.keymanager.KeyManager')
    def test_keymanager_is_created(self, keymanager_mock):
        when(self.provider)._discover_nicknym_server().thenReturn('nicknym_server')
        self.provider.provider_api_cert = 'ca_cert_path'
        self.provider.api_uri = 'api_uri'
        self.provider.api_version = '1'
        self.provider.combined_cerfificates_path = 'combined_ca_bundle'
        leap_config.gpg_binary = '/path/to/gpg'

        Keymanager(self.provider,
                   self.soledad,
                   'test_user@some-server.test',
                   self.auth.token,
                   self.auth.uuid)

        keymanager_mock.assert_called_with(
            'test_user@some-server.test',
            'nicknym_server',
            self.soledad,
            token=self.auth.token,
            ca_cert_path='ca_cert_path',
            api_uri='api_uri',
            api_version='1',
            uid=self.auth.uuid,
            gpgbinary='/path/to/gpg',
            combined_ca_bundle='combined_ca_bundle')

    def test_keymanager_generate_openpgp_key_generates_key_correctly(self):
        self.keymanager._synchronize_remote_key = MagicMock()
        when(self.keymanager)._key_exists('test_user@some-server.test').thenReturn(None)

        self.leap_keymanager.gen_key = MagicMock()
        self.leap_keymanager.send_key = MagicMock()

        self.keymanager.generate_openpgp_key()

        self.leap_keymanager.gen_key.assert_called_once()
        self.leap_keymanager.send_key.assert_called_once()

    def test_keymanager_generate_openpgp_key_doesnt_regenerate_preexisting_key(self):
        mock_open_pgp_key = MagicMock()
        mock_open_pgp_key.needs_renewal = MagicMock(return_value=False)
        when(self.keymanager)._key_exists('test_user@some-server.test').thenReturn(mock_open_pgp_key)

        self.leap_keymanager.gen_key = MagicMock()

        self.keymanager.generate_openpgp_key()

        self.leap_keymanager.gen_key.assert_not_called()

    def test_keymanager_generate_openpgp_key_doesnt_upload_preexisting_key(self):
        self.keymanager._synchronize_remote_key = MagicMock()
        mock_open_pgp_key = MagicMock()
        mock_open_pgp_key.needs_renewal = MagicMock(return_value=False)
        when(self.keymanager)._key_exists('test_user@some-server.test').thenReturn(mock_open_pgp_key)

        self.leap_keymanager.send_key = MagicMock()

        self.keymanager.generate_openpgp_key()

        self.leap_keymanager.send_key.assert_not_called()

    @defer.inlineCallbacks
    def test_keymanager_generate_openpgp_key_deletes_key_when_upload_fails(self):
        when(self.keymanager)._key_exists('test_user@some-server.test').thenReturn(None)

        self.keymanager.delete_key_pair = MagicMock()
        when(self.leap_keymanager).send_key().thenRaise(Exception('Could not upload key'))

        with self.assertRaises(UploadKeyError):
            yield self.keymanager.generate_openpgp_key()

        self.keymanager.delete_key_pair.assert_called_once()

    @defer.inlineCallbacks
    def test_keymanager_regenerate_key_pair_if_current_key_is_about_to_expire(self):
        self.keymanager._synchronize_remote_key = MagicMock()
        mock_open_pgp_key = MagicMock()
        mock_open_pgp_key.needs_renewal = MagicMock(return_value=True)
        when(self.keymanager)._key_exists('test_user@some-server.test').thenReturn(mock_open_pgp_key)

        yield self.keymanager.generate_openpgp_key()

        self.leap_keymanager.regenerate_key.assert_called_once()
        self.leap_keymanager.send_key.assert_called_once()

    @defer.inlineCallbacks
    def test_key_regeneration_does_not_delete_key_when_upload_fails(self):
        mock_open_pgp_key = MagicMock()
        mock_open_pgp_key.needs_renewal = MagicMock(return_value=True)
        when(self.keymanager)._key_exists('test_user@some-server.test').thenReturn(mock_open_pgp_key)
        when(self.leap_keymanager).send_key().thenRaise(Exception('Could not upload key'))

        self.keymanager.delete_key_pair = MagicMock()

        with self.assertRaises(UploadKeyError):
            yield self.keymanager.generate_openpgp_key()

        self.leap_keymanager.regenerate_key.assert_called_once()
        self.keymanager.delete_key_pair.assert_not_called()

    @defer.inlineCallbacks
    def test_key_is_syncronized_with_server(self):
        self.keymanager._is_key_synchronized_with_server = MagicMock(return_value=True)
        mock_open_pgp_key = MagicMock()
        mock_open_pgp_key.needs_renewal = MagicMock(return_value=False)
        when(self.keymanager)._key_exists('test_user@some-server.test').thenReturn(mock_open_pgp_key)

        yield self.keymanager.generate_openpgp_key()
        self.leap_keymanager.send_key.assert_not_called()

    @defer.inlineCallbacks
    def test_key_is_not_syncronized_with_server(self):
        self.keymanager._is_key_synchronized_with_server = MagicMock(return_value=False)
        mock_open_pgp_key = MagicMock()
        mock_open_pgp_key.needs_renewal = MagicMock(return_value=False)
        when(self.keymanager)._key_exists('test_user@some-server.test').thenReturn(mock_open_pgp_key)

        yield self.keymanager.generate_openpgp_key()
        self.leap_keymanager.send_key.assert_called_once()

    @defer.inlineCallbacks
    def test_local_and_remote_keys_are_the_same(self):
        mock_current_key = MagicMock()
        mock_current_key.fingerprint = 'ABC'
        mock_remote_key = MagicMock()
        mock_remote_key.fingerprint = 'ABC'

        self.keymanager.get_key = MagicMock(return_value=mock_remote_key)
        result = yield self.keymanager._is_key_synchronized_with_server(mock_current_key)
        self.assertTrue(result)

    @defer.inlineCallbacks
    def test_local_and_remote_keys_are_not_the_same(self):
        mock_current_key = MagicMock()
        mock_current_key.fingerprint = 'ABC'
        mock_remote_key = MagicMock()
        mock_remote_key.fingerprint = '123'

        self.keymanager.get_key = MagicMock(return_value=mock_remote_key)
        result = yield self.keymanager._is_key_synchronized_with_server(mock_current_key)
        self.assertFalse(result)
