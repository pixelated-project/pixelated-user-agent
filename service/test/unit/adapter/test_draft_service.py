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
