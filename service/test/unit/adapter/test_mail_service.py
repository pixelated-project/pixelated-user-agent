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
from twisted.trial import unittest
from pixelated.adapter.mailstore.leap_mailstore import LeapMail
from pixelated.adapter.model.mail import InputMail
from pixelated.adapter.model.status import Status

from pixelated.adapter.services.mail_service import MailService
from test.support.test_helper import mail_dict, leap_mail, duplicates_in_fields_mail_dict
from mockito import mock, unstub, when, verify, verifyNoMoreInteractions, any as ANY, never
from twisted.internet import defer


class TestMailService(unittest.TestCase):

    def setUp(self):
        self.drafts = mock()
        self.mail_store = mock()
        self.attachment_store = mock()
        self.mailboxes = mock()

        self.mailboxes.drafts = defer.succeed(self.drafts)

        self.mailboxes.trash = mock()
        self.mailboxes.sent = mock()

        self.mail_sender = mock()
        self.search_engine = mock()
        self.mail_service = MailService(
            self.mail_sender,
            self.mail_store,
            self.search_engine,
            'acount@email',
            self.attachment_store)
        self.mail = InputMail.from_dict(
            duplicates_in_fields_mail_dict(), from_address='pixelated@org')

    def tearDown(self):
        unstub()

    def test_send_mail(self):
        when(InputMail).from_dict(ANY(), ANY()).thenReturn(self.mail)
        when(self.mail_sender).sendmail(ANY()).thenReturn(defer.Deferred())

        sent_deferred = self.mail_service.send_mail(mail_dict())

        verify(self.mail_sender).sendmail(self.mail)

        sent_deferred.callback('Assume sending mail succeeded')

        return sent_deferred

    @defer.inlineCallbacks
    def test_send_mail_removes_draft(self):
        mail = LeapMail('id', 'INBOX')
        when(mail).raw = 'raw mail'
        mail._headers['To'] = []
        mail._headers['Cc'] = []
        mail._headers['Bcc'] = []
        when(InputMail).from_dict(ANY(), ANY()).thenReturn(mail)
        when(self.mail_store).delete_mail('12').thenReturn(defer.succeed(None))
        when(self.mail_store).add_mail('SENT', ANY()).thenReturn(mail)

        deferred_success = defer.succeed(None)
        when(self.mail_sender).sendmail(ANY()).thenReturn(deferred_success)

        yield self.mail_service.send_mail({'ident': '12'})

        verify(self.mail_sender).sendmail(mail)
        verify(self.mail_store).add_mail('SENT', mail.raw)
        verify(self.mail_store).delete_mail('12')

    @defer.inlineCallbacks
    def test_send_mail_marks_as_read(self):
        when(self.mail).raw = 'raw mail'
        when(InputMail).from_dict(ANY(), ANY()).thenReturn(self.mail)
        when(self.mail_store).delete_mail('12').thenReturn(defer.succeed(None))
        when(self.mail_sender).sendmail(
            self.mail).thenReturn(defer.succeed(None))

        sent_mail = LeapMail('id', 'INBOX')
        add_mail_deferral = defer.succeed(sent_mail)
        when(self.mail_store).add_mail(
            'SENT', ANY()).thenReturn(add_mail_deferral)

        yield self.mail_service.send_mail({'ident': '12'})

        self.assertIn(Status.SEEN, sent_mail.flags)
        verify(self.mail_store).update_mail(sent_mail)

    @defer.inlineCallbacks
    def test_send_mail_does_not_delete_draft_on_error(self):
        when(InputMail).from_dict(ANY(), ANY()).thenReturn(self.mail)

        deferred_failure = defer.fail(Exception("Assume sending mail failed"))
        when(self.mail_sender).sendmail(ANY()).thenReturn(deferred_failure)

        try:
            yield self.mail_service.send_mail({'ident': '12'})
            self.fail("send_mail is expected to raise if underlying call fails")
        except:
            verify(self.mail_sender).sendmail(self.mail)
            verifyNoMoreInteractions(self.drafts)

    @defer.inlineCallbacks
    def test_mark_as_read(self):
        mail = LeapMail(1, 'INBOX')
        when(self.mail_store).get_mail(1, include_body=True).thenReturn(mail)
        yield self.mail_service.mark_as_read(1)

        self.assertIn(Status.SEEN, mail.flags)
        verify(self.mail_store).update_mail(mail)

    @defer.inlineCallbacks
    def test_mark_as_unread(self):
        mail = LeapMail(1, 'INBOX')
        mail.flags.add(Status.SEEN)

        when(self.mail_store).get_mail(1, include_body=True).thenReturn(mail)
        yield self.mail_service.mark_as_unread(1)

        verify(self.mail_store).update_mail(mail)

        self.assertNotEqual(mail.status, Status.SEEN)

    @defer.inlineCallbacks
    def test_delete_mail(self):
        mail_to_delete = LeapMail(1, 'INBOX')
        when(self.mail_store).get_mail(1, include_body=True).thenReturn(
            defer.succeed(mail_to_delete))

        yield self.mail_service.delete_mail(1)

        verify(self.mail_store).move_mail_to_mailbox(1, 'TRASH')

    @defer.inlineCallbacks
    def test_delete_mail_does_not_fail_for_invalid_mail(self):
        no_mail = None
        mail_id = 1
        when(self.mail_store).get_mail(
            mail_id, include_body=True).thenReturn(defer.succeed(no_mail))

        yield self.mail_service.delete_mail(mail_id)

        verify(self.mail_store, never).delete_mail(mail_id)
        verify(self.mail_store, never).move_mail_to_mailbox(mail_id, ANY())

    @defer.inlineCallbacks
    def test_recover_mail(self):
        mail_to_recover = LeapMail(1, 'TRASH')
        when(self.mail_service).mail(1).thenReturn(mail_to_recover)
        when(self.mail_store).move_mail_to_mailbox(
            1, 'INBOX').thenReturn(mail_to_recover)

        yield self.mail_service.recover_mail(1)

        verify(self.mail_store).move_mail_to_mailbox(1, 'INBOX')

    @defer.inlineCallbacks
    def test_get_attachment(self):
        attachment_dict = {'content': bytearray(
            'data'), 'content-type': 'text/plain'}
        when(self.attachment_store).get_mail_attachment(
            'some attachment id').thenReturn(defer.succeed(attachment_dict))

        attachment = yield self.mail_service.attachment('some attachment id')

        self.assertEqual(attachment_dict, attachment)

    @defer.inlineCallbacks
    def test_update_tags_return_a_set_with_the_current_tags(self):
        mail = LeapMail(1, 'INBOX', tags={'custom_1', 'custom_2'})
        when(self.mail_store).get_mail(1, include_body=True).thenReturn(mail)
        when(self.search_engine).tags(
            query='', skip_default_tags=True).thenReturn([])

        updated_mail = yield self.mail_service.update_tags(1, {'custom_1', 'custom_3'})

        verify(self.mail_store).update_mail(mail)
        self.assertEqual({'custom_1', 'custom_3'}, updated_mail.tags)

    @defer.inlineCallbacks
    def test_if_recipient_doubled_in_fields_send_only_in_bcc(self):
        mail = InputMail.from_dict(
            duplicates_in_fields_mail_dict(), from_address='pixelated@org')

        yield self.mail_service._deduplicate_recipients(mail)

        self.assertIn('to@pixelated.org', mail.to)
        self.assertNotIn('another@pixelated.org', mail.to)
        self.assertIn('another@pixelated.org', mail.bcc)

    @defer.inlineCallbacks
    def test_if_recipient_doubled_in_fields_send_only_in_to(self):
        mail = InputMail.from_dict(
            duplicates_in_fields_mail_dict(), from_address='pixelated@org')

        yield self.mail_service._deduplicate_recipients(mail)

        self.assertIn('third@pixelated.org', mail.to)
        self.assertNotIn('third@pixelated.org', mail.cc)
        self.assertIn('cc@pixelated.org', mail.cc)
        self.assertNotIn('another@pixelated.org', mail.cc)

    @defer.inlineCallbacks
    def test_if_deduplicates_when_recipient_repeated_in_field(self):
        mail = InputMail.from_dict(
            duplicates_in_fields_mail_dict(), from_address='pixelated@org')

        yield self.mail_service._deduplicate_recipients(mail)

        self.assertItemsEqual(
            ['bcc@pixelated.org', 'another@pixelated.org'], mail.bcc)
        self.assertItemsEqual(
            ['third@pixelated.org', 'to@pixelated.org'], mail.to)
        self.assertItemsEqual(['cc@pixelated.org'], mail.cc)

    def test_remove_canonical_recipient_when_it_is_not_canonical(self):
        recipient = u'user@pixelated.org'

        non_canonical = self.mail_service._remove_canonical_recipient(
            recipient)

        self.assertEqual(recipient, non_canonical)

    def test_remove_canonical_recipient_when_it_is_canonical(self):
        recipient = u'User <user@pixelated.org>'

        non_canonical = self.mail_service._remove_canonical_recipient(
            recipient)

        self.assertEqual(u'user@pixelated.org', non_canonical)
