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
# MERCHANTABILITY or FITNESS FOR A PCULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Pixelated. If not, see <http://www.gnu.org/licenses/>.
from twisted.internet.defer import inlineCallbacks


class MailboxIndexerListener(object):
    """ Listens for new mails, keeping the index updated """

    SEARCH_ENGINE = None

    @classmethod
    @inlineCallbacks
    def listen(cls, account, mailbox_name, soledad_querier):
        listener = MailboxIndexerListener(mailbox_name, soledad_querier)
        mbx = yield account.getMailbox(mailbox_name)
        if listener not in mbx.listeners:
            mbx.addListener(listener)

    def __init__(self, mailbox_name, soledad_querier):
        self.mailbox_name = mailbox_name
        self.querier = soledad_querier

    def newMessages(self, exists, recent):
        indexed_idents = set(self.SEARCH_ENGINE.search('tag:' + self.mailbox_name.lower(), all_mails=True))
        soledad_idents = self.querier.idents_by_mailbox(self.mailbox_name)

        missing_idents = soledad_idents.difference(indexed_idents)

        self.SEARCH_ENGINE.index_mails(self.querier.mails(missing_idents))

    def __eq__(self, other):
        return other and other.mailbox_name == self.mailbox_name

    def __hash__(self):
        return self.mailbox_name.__hash__()

    def __repr__(self):
        return 'MailboxListener: ' + self.mailbox_name
