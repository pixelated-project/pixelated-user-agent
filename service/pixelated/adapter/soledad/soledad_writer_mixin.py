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


class SoledadWriterMixin(SoledadDbFacadeMixin, object):

    def mark_all_as_not_recent(self):
        for mailbox in ['INBOX', 'DRAFTS', 'SENT', 'TRASH']:
            rct = self.get_recent_by_mbox(mailbox)
            if not rct or not rct[0].content['rct']:
                return
            rct = rct[0]
            rct.content['rct'] = []
            self.put_doc(rct)

    def save_mail(self, mail):
        self.put_doc(mail.fdoc)

    def create_mail(self, mail, mailbox_name):
        mbox_doc = self.get_mbox(mailbox_name)[0]
        uid = self.get_lastuid(mbox_doc)

        [self.create_doc(doc) for doc in mail.get_for_save(next_uid=uid, mailbox=mailbox_name)]

        mbox_doc.content['lastuid'] = uid + 1
        self.put_doc(mbox_doc)

        return self.mail(mail.ident)

    def remove_mail(self, mail):
        # FIX-ME: Must go through all the part_map phash to delete all the cdocs
        self.delete_doc(mail.fdoc)
        self.delete_doc(mail.hdoc)
        self.delete_doc(mail.bdoc)
