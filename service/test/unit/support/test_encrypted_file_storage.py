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
import shutil
from twisted.trial import unittest
from pixelated.support.encrypted_file_storage import EncryptedFileStorage


class EncryptedFileStorageTest(unittest.TestCase):

    def setUp(self):
        self.key = '2\x06\xf87F:\xd2\xe2]w\xc9\x0c\xb8\x9b\x8e\xd3\x92\t\xabHu\xa6\xa3\x9a\x8d\xec\x0c\xab<8\xbb\x12\xfbP\xf2\x83"\xa1\xcf7\x92\xb0!\xfe\xebM\x80\x8a\x14\xe6\xf9xr\xf5#\x8f\x1bs\xb3#\x0e)a\xd8'
        self.msg = 'this is a very, very secret binary message: \xbe\xba\xca\xfe'
        self.path = os.path.join('tmp', 'search_test')
        self._cleanup_path()
        self.storage = EncryptedFileStorage(self.path, self.key)

    def tearDown(self):
        self._cleanup_path()

    def _cleanup_path(self):
        if os.path.exists(self.path):
            shutil.rmtree(self.path)

    def test_encrypt_decrypt(self):
        storage, msg = self.storage, self.msg

        ciphertext = storage.encrypt(msg)

        self.assertNotEquals(msg, ciphertext)
        self.assertEquals(msg, storage.decrypt(ciphertext))

    def test_mac_against_appended_garbage(self):
        storage, msg = self.storage, self.msg

        ciphertext = storage.encrypt(msg)
        corrupted_ciphertext = ciphertext + 'garbage'

        try:
            storage.decrypt(corrupted_ciphertext)
            self.fail('MAC is not detecting appended garbage on ciphertext')
        except:
            pass

    def test_mac_against_modified_file(self):
        storage, msg = self.storage, self.msg

        ciphertext = storage.encrypt(msg)
        corrupted_ciphertext = ''.join([chr(ord(i) >> 1) for i in ciphertext])

        try:
            storage.decrypt(corrupted_ciphertext)
            self.fail('MAC is not detecting corrupt ciphertext')
        except:
            pass
