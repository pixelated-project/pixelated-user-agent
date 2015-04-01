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


class SoledadDbFacadeMixin(object):

    def get_all_flags(self):
        return self.soledad.get_from_index('by-type', 'flags')

    def get_all_flags_by_mbox(self, mbox):
        return self.soledad.get_from_index('by-type-and-mbox', 'flags', mbox) if mbox else []

    def get_content_by_phash(self, phash):
        content = self.soledad.get_from_index('by-type-and-payloadhash', 'cnt', phash) if phash else []
        if len(content):
            return content[0]

    def get_flags_by_chash(self, chash):
        flags = self.soledad.get_from_index('by-type-and-contenthash', 'flags', chash) if chash else []
        if len(flags):
            return flags[0]

    def get_header_by_chash(self, chash):
        header = self.soledad.get_from_index('by-type-and-contenthash', 'head', chash) if chash else []
        if len(header):
            return header[0]

    def get_recent_by_mbox(self, mbox):
        return self.soledad.get_from_index('by-type-and-mbox', 'rct', mbox) if mbox else []

    def put_doc(self, doc):
        return self.soledad.put_doc(doc)

    def create_doc(self, doc):
        return self.soledad.create_doc(doc)

    def delete_doc(self, doc):
        return self.soledad.delete_doc(doc)

    def idents_by_mailbox(self, mbox):
        return set(doc.content['chash'] for doc in self.soledad.get_from_index('by-type-and-mbox-and-deleted', 'flags', mbox, '0')) if mbox else set()

    def get_all_mbox(self):
        return self.soledad.get_from_index('by-type', 'mbox')

    def get_mbox(self, mbox):
        return self.soledad.get_from_index('by-type-and-mbox', 'mbox', mbox) if mbox else []

    def get_lastuid(self, mbox):
        if isinstance(mbox, str):
            mbox = self.get_mbox(mbox)[0]
        return mbox.content['lastuid']

    def get_search_index_masterkey(self):
        return self.soledad.get_from_index('by-type', 'index_key')
