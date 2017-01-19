#
# Copyright (c) 2015 ThoughtWorks, Inc.
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

from twisted.trial import unittest
from twisted.internet import defer
from pixelated.adapter.mailstore.leap_mailstore import LeapMail

from pixelated.adapter.model.mail import InputMail
from pixelated.adapter.services.draft_service import DraftService
import test.support.test_helper as test_helper
from mockito import mock, verify, inorder, when


class DraftServiceTest(unittest.TestCase):

    def setUp(self):
        self.mailboxes = mock()
        self.mail_store = mock()
        self.draft_service = DraftService(self.mail_store)

    def test_add_draft(self):
        mail = InputMail()
        self.draft_service.create_draft(mail)

        verify(self.mail_store).add_mail('DRAFTS', mail.raw)

    def test_update_draft(self):
        mail = InputMail.from_dict(test_helper.mail_dict(), from_address='pixelated@org')
        when(self.mail_store).delete_mail(mail.ident).thenReturn(defer.succeed(True))
        when(self.mail_store).add_mail('DRAFTS', mail.raw).thenReturn(defer.succeed(LeapMail('id', 'DRAFTS')))

        self.draft_service.update_draft(mail.ident, mail)

        inorder.verify(self.mail_store).delete_mail(mail.ident)
        inorder.verify(self.mail_store).add_mail('DRAFTS', mail.raw)
