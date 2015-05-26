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
from pixelated.adapter.soledad.soledad_duplicate_removal_mixin import SoledadDuplicateRemovalMixin
from pixelated.adapter.soledad.soledad_reader_mixin import SoledadReaderMixin
from pixelated.adapter.soledad.soledad_search_key_masterkey_retrieval_mixin import SoledadSearchIndexMasterkeyRetrievalMixin
from pixelated.adapter.soledad.soledad_writer_mixin import SoledadWriterMixin


class SoledadQuerier(SoledadWriterMixin,
                     SoledadReaderMixin,
                     SoledadDuplicateRemovalMixin,
                     SoledadSearchIndexMasterkeyRetrievalMixin,
                     object):

    def __init__(self, soledad):
        self.soledad = soledad
