# -*- coding: utf-8 -*-
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
import base64
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import quopri
from uuid import uuid4
from email.parser import Parser
import os
from leap.soledad.common.document import SoledadDocument
from leap.bitmask.mail.adaptors.soledad_indexes import MAIL_INDEXES
from twisted.internet.defer import FirstError
from twisted.trial.unittest import TestCase
from leap.bitmask.mail import constants
from twisted.internet import defer
from mock import patch
from mockito import mock, when, verify, any as ANY
from leap.bitmask.mail.adaptors.soledad import SoledadMailAdaptor, MailboxWrapper, ContentDocWrapper
import pkg_resources
from leap.bitmask.mail.mail import Message
from pixelated.adapter.mailstore import underscore_uuid

from pixelated.adapter.mailstore.leap_mailstore import LeapMailStore, LeapMail
from test.support.mockito import AnswerSelector


class TestLeapMailStore(TestCase):
    def setUp(self):
        self.soledad = mock()
        self.mbox_uuid = str(uuid4())
        self.doc_by_id = {}
        self.mbox_uuid_by_name = {}
        self.mbox_soledad_docs = []

        with patch('mockito.invocation.AnswerSelector', AnswerSelector):
            when(self.soledad).get_from_index('by-type', 'mbox').thenAnswer(lambda: defer.succeed(self.mbox_soledad_docs))
        self._mock_get_mailbox('INBOX')

    @defer.inlineCallbacks
    def test_get_mail_not_exist(self):
        with patch('mockito.invocation.AnswerSelector', AnswerSelector):
            when(self.soledad).get_doc(ANY()).thenAnswer(lambda: defer.succeed(None))
        store = LeapMailStore(self.soledad)

        mail = yield store.get_mail(_format_mdoc_id(uuid4(), 1))

        self.assertIsNone(mail)

    @defer.inlineCallbacks
    def test_get_mail(self):
        mdoc_id, _ = self._add_mail_fixture_to_soledad_from_file('mbox00000000')

        store = LeapMailStore(self.soledad)

        mail = yield store.get_mail(mdoc_id)

        self.assertIsInstance(mail, LeapMail)
        self.assertEqual('darby.senger@zemlak.biz', mail.from_sender)
        self.assertEqual(['carmel@murazikortiz.name'], mail.to)
        self.assertEqual('Itaque consequatur repellendus provident sunt quia.', mail.subject)
        self.assertIsNone(mail.body)
        self.assertEqual('INBOX', mail.mailbox_name)

    @defer.inlineCallbacks
    def test_get_mail_from_mailbox(self):
        other, _ = self._mock_get_mailbox('OTHER', create_new_uuid=True)
        mdoc_id, _ = self._add_mail_fixture_to_soledad_from_file('mbox00000000', other.uuid)

        store = LeapMailStore(self.soledad)

        mail = yield store.get_mail(mdoc_id)

        self.assertEqual('OTHER', mail.mailbox_name)

    @defer.inlineCallbacks
    def test_get_two_different_mails(self):
        first_mdoc_id, _ = self._add_mail_fixture_to_soledad_from_file('mbox00000000')
        second_mdoc_id, _ = self._add_mail_fixture_to_soledad_from_file('mbox00000001')

        store = LeapMailStore(self.soledad)

        mail1 = yield store.get_mail(first_mdoc_id)
        mail2 = yield store.get_mail(second_mdoc_id)

        self.assertNotEqual(mail1, mail2)
        self.assertEqual('Itaque consequatur repellendus provident sunt quia.', mail1.subject)
        self.assertEqual('Error illum dignissimos autem eos aspernatur.', mail2.subject)

    @defer.inlineCallbacks
    def test_get_mails(self):
        first_mdoc_id, _ = self._add_mail_fixture_to_soledad_from_file('mbox00000000')
        second_mdoc_id, _ = self._add_mail_fixture_to_soledad_from_file('mbox00000001')

        store = LeapMailStore(self.soledad)

        mails = yield store.get_mails([first_mdoc_id, second_mdoc_id])

        self.assertEqual(2, len(mails))
        self.assertEqual('Itaque consequatur repellendus provident sunt quia.', mails[0].subject)
        self.assertEqual('Error illum dignissimos autem eos aspernatur.', mails[1].subject)

    @defer.inlineCallbacks
    def test_get_mails_fails_for_invalid_mail_id(self):
        store = LeapMailStore(self.soledad)

        try:
            yield store.get_mails(['invalid'])
            self.fail('Exception expected')
        except Exception, e:
            pass

    @defer.inlineCallbacks
    def test_get_mail_with_body(self):
        expeted_body = 'Dignissimos ducimus veritatis. Est tenetur consequatur quia occaecati. Vel sit sit voluptas.\n\nEarum distinctio eos. Accusantium qui sint ut quia assumenda. Facere dignissimos inventore autem sit amet. Pariatur voluptatem sint est.\n\nUt recusandae praesentium aspernatur. Exercitationem amet placeat deserunt quae consequatur eum. Unde doloremque suscipit quia.\n\n'
        mdoc_id, _ = self._add_mail_fixture_to_soledad_from_file('mbox00000000')

        store = LeapMailStore(self.soledad)

        mail = yield store.get_mail(mdoc_id, include_body=True)

        self.assertEqual(expeted_body, mail.body)

    @defer.inlineCallbacks
    def test_update_mail(self):
        mdoc_id, fdoc_id = self._add_mail_fixture_to_soledad_from_file('mbox00000000')
        soledad_fdoc = self.doc_by_id[fdoc_id]
        when(self.soledad).put_doc(soledad_fdoc).thenReturn(defer.succeed(None))

        store = LeapMailStore(self.soledad)

        mail = yield store.get_mail(mdoc_id)

        mail.tags.add('new_tag')

        yield store.update_mail(mail)

        verify(self.soledad).put_doc(soledad_fdoc)
        self.assertTrue('new_tag' in soledad_fdoc.content['tags'])

    @defer.inlineCallbacks
    def test_all_mails(self):
        first_mdoc_id, _ = self._add_mail_fixture_to_soledad_from_file('mbox00000000')
        second_mdoc_id, _ = self._add_mail_fixture_to_soledad_from_file('mbox00000001')
        when(self.soledad).get_from_index('by-type', 'meta').thenReturn(defer.succeed([self.doc_by_id[first_mdoc_id], self.doc_by_id[second_mdoc_id]]))

        store = LeapMailStore(self.soledad)

        mails = yield store.all_mails()

        self.assertIsNotNone(mails)
        self.assertEqual(2, len(mails))
        self.assertEqual('Itaque consequatur repellendus provident sunt quia.', mails[0].subject)
        self.assertEqual('Error illum dignissimos autem eos aspernatur.', mails[1].subject)

    @defer.inlineCallbacks
    def test_add_mailbox(self):
        when(self.soledad).list_indexes().thenReturn(defer.succeed(MAIL_INDEXES)).thenReturn(defer.succeed(MAIL_INDEXES))
        when(self.soledad).get_from_index('by-type-and-mbox', 'mbox', 'TEST').thenReturn(defer.succeed([]))
        self._mock_create_soledad_doc(self.mbox_uuid, MailboxWrapper(mbox='TEST'))
        with patch('mockito.invocation.AnswerSelector', AnswerSelector):
            when(self.soledad).get_doc(self.mbox_uuid).thenAnswer(lambda: defer.succeed(self.doc_by_id[self.mbox_uuid]))
            when(self.soledad).put_doc(ANY()).thenAnswer(lambda: defer.succeed(None))
        store = LeapMailStore(self.soledad)

        mbox = yield store.add_mailbox('TEST')

        self.assertIsNotNone(mbox)
        self.assertEqual(self.mbox_uuid, mbox.doc_id)
        self.assertEqual('TEST', mbox.mbox)
        self.assertIsNotNone(mbox.uuid)
        # assert index got updated

    @defer.inlineCallbacks
    def test_get_mailbox_names_always_contains_inbox(self):
        store = LeapMailStore(self.soledad)

        names = yield store.get_mailbox_names()

        self.assertEqual({'INBOX'}, names)

    @defer.inlineCallbacks
    def test_get_mailbox_names(self):
        self._mock_get_mailbox('OTHER', create_new_uuid=True)
        store = LeapMailStore(self.soledad)

        names = yield store.get_mailbox_names()

        self.assertEqual({'INBOX', 'OTHER'}, names)

    @defer.inlineCallbacks
    def test_handles_unmapped_mailbox_uuid(self):
        # given
        store = LeapMailStore(self.soledad)
        new_uuid = 'UNICORN'

        # if no mailbox doc is created yet (async hell?)
        when(self.soledad).get_from_index('by-type', 'mbox').thenReturn(defer.succeed([]))

        # then it should point to empty, which is all mails
        name = yield store._mailbox_name_from_uuid(new_uuid)
        self.assertEquals('', name)

    @defer.inlineCallbacks
    def test_add_mail(self):
        expected_message = self._add_create_mail_mocks_to_soledad_from_fixture_file('mbox00000000')
        mail = self._load_mail_from_file('mbox00000000')
        self._mock_get_mailbox('INBOX')

        store = LeapMailStore(self.soledad)

        message = yield store.add_mail('INBOX', mail.as_string())

        self.assertIsInstance(message, LeapMail)
        self._assert_message_docs_created(expected_message, message)

    @defer.inlineCallbacks
    def test_add_mail_with_attachment(self):
        input_mail = MIMEMultipart()
        input_mail.attach(MIMEText(u'a utf8 message', _charset='utf-8'))
        attachment = MIMEApplication('pretend to be binary attachment data')
        attachment.add_header('Content-Disposition', 'attachment', filename='filename.txt')
        input_mail.attach(attachment)
        mocked_message = self._add_create_mail_mocks_to_soledad(input_mail)
        store = LeapMailStore(self.soledad)

        message = yield store.add_mail('INBOX', input_mail.as_string())

        expected = [{'ident': self._cdoc_phash_from_message(mocked_message, 2), 'name': 'filename.txt', 'encoding': 'base64', 'size': 48, 'content-type': 'application/octet-stream'}]
        self.assertEqual(expected, message.as_dict()['attachments'])

    @defer.inlineCallbacks
    def test_add_mail_with_inline_attachment(self):
        input_mail = MIMEMultipart()
        input_mail.attach(MIMEText(u'a utf8 message', _charset='utf-8'))
        attachment = MIMEApplication('pretend to be an inline attachment')
        attachment.add_header('Content-Disposition', 'u\'inline;\n\tfilename=super_nice_photo.jpg')
        input_mail.attach(attachment)
        mocked_message = self._add_create_mail_mocks_to_soledad(input_mail)
        store = LeapMailStore(self.soledad)

        message = yield store.add_mail('INBOX', input_mail.as_string())

        expected = [{'ident': self._cdoc_phash_from_message(mocked_message, 2), 'name': 'super_nice_photo.jpg', 'encoding': 'base64', 'size': 48, 'content-type': 'application/octet-stream'}]
        self.assertEqual(expected, message.as_dict()['attachments'])

    @defer.inlineCallbacks
    def test_add_mail_with_nested_attachments(self):
        input_mail = MIMEMultipart()
        input_mail.attach(MIMEText(u'a utf8 message', _charset='utf-8'))
        attachment = MIMEApplication('pretend to be binary attachment data')
        attachment.add_header('Content-Disposition', 'attachment', filename='filename.txt')
        nested_attachment = MIMEMultipart()
        nested_attachment.attach(attachment)
        input_mail.attach(nested_attachment)
        mocked_message = self._add_create_mail_mocks_to_soledad(input_mail)
        store = LeapMailStore(self.soledad)

        message = yield store.add_mail('INBOX', input_mail.as_string())

        expected = [{'ident': self._cdoc_phash_from_message(mocked_message, 2), 'name': 'filename.txt', 'encoding': 'base64', 'size': 48, 'content-type': 'application/octet-stream'}]
        self.assertEqual(expected, message.as_dict()['attachments'])

    def test_extract_attachment_filename_with_or_without_quotes(self):
        input_mail = MIMEMultipart()
        input_mail.attach(MIMEText(u'a utf8 message', _charset='utf-8'))

        attachment_without_quotes = MIMEApplication('pretend to be an attachment from apple mail')
        attachment_without_quotes.add_header('Content-Disposition', 'u\'attachment;\n\tfilename=batatinha.rtf')
        input_mail.attach(attachment_without_quotes)

        attachment_with_quotes = MIMEApplication('pretend to be an attachment from thunderbird')
        attachment_with_quotes.add_header('Content-Disposition', 'u\'attachment; filename="receipt.pdf"')
        input_mail.attach(attachment_with_quotes)

        message = self._add_create_mail_mocks_to_soledad(input_mail)
        store = LeapMailStore(self.soledad)
        attachment_info = store._extract_attachment_info_from(message)

        self.assertEqual('batatinha.rtf', attachment_info[0].name)
        self.assertEqual('receipt.pdf', attachment_info[1].name)

    def test_extract_attachment_filename_from_other_headers(self):
        input_mail = MIMEMultipart()
        input_mail.attach(MIMEText(u'a utf8 message', _charset='utf-8'))

        attachment_without_description = MIMEApplication('pretend to be an attachment from apple mail', _subtype='pgp-keys')
        attachment_without_description.add_header('Content-Disposition', 'attachment')
        attachment_without_description.add_header('Content-Description', 'Some GPG Key')

        input_mail.attach(attachment_without_description)

        attachment_with_name_in_content_type = MIMEApplication('pretend to be an attachment from thunderbird', _subtype='pgp-signature; name="signature.asc"')
        attachment_with_name_in_content_type.add_header('Content-Disposition', 'inline')
        input_mail.attach(attachment_with_name_in_content_type)

        message = self._add_create_mail_mocks_to_soledad(input_mail)
        store = LeapMailStore(self.soledad)
        attachment_info = store._extract_attachment_info_from(message)

        self.assertEqual('Some GPG Key', attachment_info[0].name)
        self.assertEqual('signature.asc', attachment_info[1].name)

    @defer.inlineCallbacks
    def test_add_mail_with_special_chars(self):
        input_mail = MIMEText(u'a utf8 message', _charset='utf-8')
        input_mail['From'] = Header(u'"Älbert Übrö" <äüö@example.mail>', 'iso-8859-1')
        input_mail['Subject'] = Header(u'Hällö Wörld', 'iso-8859-1')
        self._add_create_mail_mocks_to_soledad(input_mail)
        store = LeapMailStore(self.soledad)

        message = yield store.add_mail('INBOX', input_mail.as_string())

        self.assertEqual(u'"\xc4lbert \xdcbr\xf6" <\xe4\xfc\xf6@example.mail>', message.as_dict()['header']['from'])

    def _cdoc_phash_from_message(self, mocked_message, attachment_nr):
        return mocked_message.get_wrapper().cdocs[attachment_nr].future_doc_id[2:]

    @defer.inlineCallbacks
    def test_delete_mail(self):
        mdoc_id, fdoc_id = self._add_mail_fixture_to_soledad_from_file('mbox00000000')

        store = LeapMailStore(self.soledad)

        yield store.delete_mail(mdoc_id)

        self._assert_mail_got_deleted(fdoc_id, mdoc_id)

    @defer.inlineCallbacks
    def test_get_mailbox_mail_ids(self):
        mdoc_id, fdoc_id = self._add_mail_fixture_to_soledad_from_file('mbox00000000')
        when(self.soledad).get_from_index('by-type-and-mbox-uuid', 'flags', underscore_uuid(self.mbox_uuid)).thenReturn(defer.succeed([self.doc_by_id[fdoc_id]]))
        self._mock_get_mailbox('INBOX')
        store = LeapMailStore(self.soledad)

        mail_ids = yield store.get_mailbox_mail_ids('INBOX')

        self.assertEqual(1, len(mail_ids))
        self.assertEqual(mdoc_id, mail_ids[0])

    @defer.inlineCallbacks
    def test_delete_mailbox(self):
        _, mbox_soledad_doc = self._mock_get_mailbox('INBOX')
        store = LeapMailStore(self.soledad)
        when(self.soledad).delete_doc(mbox_soledad_doc).thenReturn(defer.succeed(None))

        yield store.delete_mailbox('INBOX')

        verify(self.soledad).delete_doc(self.doc_by_id[mbox_soledad_doc.doc_id])
        # should also verify index is updated

    @defer.inlineCallbacks
    def test_copy_mail_to_mailbox(self):
        expected_message = self._add_create_mail_mocks_to_soledad_from_fixture_file('mbox00000000')
        mail_id, fdoc_id = self._add_mail_fixture_to_soledad_from_file('mbox00000000')
        self._mock_get_mailbox('TRASH')
        store = LeapMailStore(self.soledad)

        mail = yield store.copy_mail_to_mailbox(mail_id, 'TRASH')

        self._assert_message_docs_created(expected_message, mail, only_mdoc_and_fdoc=True)

    @defer.inlineCallbacks
    def test_move_to_mailbox(self):
        expected_message = self._add_create_mail_mocks_to_soledad_from_fixture_file('mbox00000000')
        mail_id, fdoc_id = self._add_mail_fixture_to_soledad_from_file('mbox00000000')
        self._mock_get_mailbox('TRASH')
        store = LeapMailStore(self.soledad)

        mail = yield store.move_mail_to_mailbox(mail_id, 'TRASH')

        self._assert_message_docs_created(expected_message, mail, only_mdoc_and_fdoc=True)
        self._assert_mail_got_deleted(fdoc_id, mail_id)

    @defer.inlineCallbacks
    def test_all_mail_graceful_error_handling(self):
        mail_id, fdoc_id = self._add_mail_fixture_to_soledad_from_file('mbox00000000')
        when(self.soledad).get_from_index('by-type', 'meta').thenReturn(defer.succeed([self.doc_by_id[mail_id]]))
        with patch('mockito.invocation.AnswerSelector', AnswerSelector):
            when(self.soledad).get_doc(self.doc_by_id[mail_id].content['cdocs'][0]).thenAnswer(lambda: defer.fail(Exception('fail loading attachment')))
        store = LeapMailStore(self.soledad)

        mails = yield store.all_mails(gracefully_ignore_errors=True)

        self.assertEqual(0, len(mails))

    def _assert_mail_got_deleted(self, fdoc_id, mail_id):
        verify(self.soledad).delete_doc(self.doc_by_id[mail_id])
        verify(self.soledad).delete_doc(self.doc_by_id[fdoc_id])

    def _assert_message_docs_created(self, expected_message, actual_message, only_mdoc_and_fdoc=False):
        wrapper = expected_message.get_wrapper()

        verify(self.soledad).create_doc(wrapper.mdoc.serialize(), doc_id=actual_message.mail_id)
        verify(self.soledad).create_doc(wrapper.fdoc.serialize(), doc_id=wrapper.fdoc.future_doc_id)
        if not only_mdoc_and_fdoc:
            verify(self.soledad).create_doc(wrapper.hdoc.serialize(), doc_id=wrapper.hdoc.future_doc_id)
            for nr, cdoc in wrapper.cdocs.items():
                verify(self.soledad).create_doc(cdoc.serialize(), doc_id=wrapper.cdocs[nr].future_doc_id)

    def _mock_get_mailbox(self, mailbox_name, create_new_uuid=False):
        mbox_uuid = self.mbox_uuid if not create_new_uuid else str(uuid4())
        when(self.soledad).list_indexes().thenReturn(defer.succeed(MAIL_INDEXES)).thenReturn(
            defer.succeed(MAIL_INDEXES))
        doc_id = str(uuid4())
        mbox = MailboxWrapper(doc_id=doc_id, mbox=mailbox_name, uuid=mbox_uuid)
        soledad_doc = SoledadDocument(doc_id, json=json.dumps(mbox.serialize()))
        when(self.soledad).get_from_index('by-type-and-mbox', 'mbox', mailbox_name).thenReturn(defer.succeed([soledad_doc]))
        self._mock_get_soledad_doc(doc_id, mbox)

        self.mbox_uuid_by_name[mailbox_name] = mbox_uuid
        self.mbox_soledad_docs.append(soledad_doc)

        return mbox, soledad_doc

    def _add_mail_fixture_to_soledad_from_file(self, mail_file, mbox_uuid=None):
        mail = self._load_mail_from_file(mail_file)
        return self._add_mail_fixture_to_soledad(mail, mbox_uuid)

    def _add_mail_fixture_to_soledad(self, mail, mbox_uuid=None):
        msg = self._convert_mail_to_leap_message(mail, mbox_uuid)
        wrapper = msg.get_wrapper()
        mdoc_id = wrapper.mdoc.future_doc_id
        fdoc_id = wrapper.mdoc.fdoc
        hdoc_id = wrapper.mdoc.hdoc
        cdoc_id = wrapper.mdoc.cdocs[0]

        self._mock_get_soledad_doc(mdoc_id, wrapper.mdoc)
        self._mock_get_soledad_doc(fdoc_id, wrapper.fdoc)
        self._mock_get_soledad_doc(hdoc_id, wrapper.hdoc)
        self._mock_get_soledad_doc(cdoc_id, wrapper.cdocs[1])
        return mdoc_id, fdoc_id

    def _add_create_mail_mocks_to_soledad_from_fixture_file(self, mail_file):
        mail = self._load_mail_from_file(mail_file)
        return self._add_create_mail_mocks_to_soledad(mail)

    def _add_create_mail_mocks_to_soledad(self, example_mail):
        mail = self._convert_mail_to_leap_message(example_mail)
        wrapper = mail.get_wrapper()

        mdoc_id = wrapper.mdoc.future_doc_id
        fdoc_id = wrapper.mdoc.fdoc
        hdoc_id = wrapper.mdoc.hdoc

        self._mock_create_soledad_doc(mdoc_id, wrapper.mdoc)
        self._mock_create_soledad_doc(fdoc_id, wrapper.fdoc)
        self._mock_create_soledad_doc(hdoc_id, wrapper.hdoc)

        for _, cdoc in wrapper.cdocs.items():
            self._mock_create_soledad_doc(cdoc.future_doc_id, cdoc)
            self._mock_get_soledad_doc(cdoc.future_doc_id, cdoc)

        return mail

    def _convert_mail_to_leap_message(self, mail, mbox_uuid=None):
        msg = SoledadMailAdaptor().get_msg_from_string(Message, mail.as_string())
        if mbox_uuid is None:
            msg.get_wrapper().set_mbox_uuid(self.mbox_uuid)
        else:
            msg.get_wrapper().set_mbox_uuid(mbox_uuid)

        return msg

    def _mock_get_soledad_doc(self, doc_id, doc):
        soledad_doc = SoledadDocument(doc_id, json=json.dumps(doc.serialize()))

        with patch('mockito.invocation.AnswerSelector', AnswerSelector):
            when(self.soledad).get_doc(doc_id).thenAnswer(lambda: defer.succeed(soledad_doc))

        self.doc_by_id[doc_id] = soledad_doc

    def _mock_create_soledad_doc(self, doc_id, doc):
        soledad_doc = SoledadDocument(doc_id, json=json.dumps(doc.serialize()))
        if doc.future_doc_id:
            when(self.soledad).create_doc(doc.serialize(), doc_id=doc_id).thenReturn(defer.succeed(soledad_doc))
        else:
            when(self.soledad).create_doc(doc.serialize()).thenReturn(defer.succeed(soledad_doc))
        self.doc_by_id[doc_id] = soledad_doc

    def _load_mail_from_file(self, mail_file):
        mailset_dir = pkg_resources.resource_filename('test.unit.fixtures', 'mailset')
        mail_file = os.path.join(mailset_dir, 'new', mail_file)
        with open(mail_file) as f:
            mail = Parser().parse(f)
        return mail


def _format_mdoc_id(mbox_uuid, chash):
    return constants.METAMSGID.format(mbox_uuid=mbox_uuid, chash=chash)
