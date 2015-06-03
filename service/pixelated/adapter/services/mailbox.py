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
from twisted.internet import defer


class Mailbox(object):

    def __init__(self, mailbox_name, querier, search_engine):
        self.mailbox_name = mailbox_name
        self.mailbox_tag = mailbox_name.lower()
        self.search_engine = search_engine
        self.querier = querier

    @property
    def fresh(self):
        return self.querier.get_lastuid(self.mailbox_name) == 0

    def mail(self, mail_id):
        return self.querier.mail(mail_id)

    @defer.inlineCallbacks
    def add(self, mail):
        added_mail = yield self.querier.create_mail(mail, self.mailbox_name)
        self.search_engine.index_mail(added_mail)
        defer.returnValue(added_mail)

    def remove(self, ident):
        mail = self.querier.mail(ident)
        self.search_engine.remove_from_index(mail.ident)
        mail.remove_all_tags()
        self.querier.remove_mail(mail)

    @classmethod
    def create(cls, mailbox_name, soledad_querier, search_engine):
        return Mailbox(mailbox_name, soledad_querier, search_engine)
