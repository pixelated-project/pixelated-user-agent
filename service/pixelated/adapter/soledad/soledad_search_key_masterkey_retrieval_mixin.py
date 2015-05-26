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
from pixelated.adapter.soledad.soledad_facade_mixin import SoledadDbFacadeMixin
import os
import base64
from twisted.internet import defer


class SoledadSearchIndexMasterkeyRetrievalMixin(SoledadDbFacadeMixin, object):

    def get_index_masterkey(self):
        deferred = self.get_search_index_masterkey()
        deferred.addCallback(self._ensure_masterkey_exists)
        return deferred

    def _ensure_masterkey_exists(self, result):
        index_key_doc = result[0] if result else None

        if not index_key_doc:
            new_index_key = os.urandom(64)  # 32 for encryption, 32 for hmac
            self.create_doc(dict(type='index_key', value=base64.encodestring(new_index_key)))
            return new_index_key
        return base64.decodestring(index_key_doc.content['value'])
