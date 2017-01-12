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
import json
from uuid import uuid4

from leap.soledad.common import l2db
from leap.bitmask.mail.adaptors.soledad_indexes import MAIL_INDEXES
from leap.soledad.common.document import SoledadDocument
from mock import patch
from mockito import mock, when, verify
from twisted.internet import defer
from twisted.trial.unittest import TestCase
from leap.bitmask.mail.adaptors.soledad import SoledadMailAdaptor, MailboxWrapper, ContentDocWrapper

from pixelated.adapter.mailstore.leap_attachment_store import LeapAttachmentStore
from test.support.mockito import AnswerSelector


class TestLeapAttachmentStore(TestCase):
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
    def test_get_mail_attachment(self):
        attachment_id = 'AAAA9AAD9E153D24265395203C53884506ABA276394B9FEC02B214BF9E77E48E'
        doc = SoledadDocument(json=json.dumps({'content_type': 'foo/bar', 'raw': 'asdf'}))
        when(self.soledad).get_from_index('by-type-and-payloadhash', 'cnt', attachment_id).thenReturn(defer.succeed([doc]))
        store = LeapAttachmentStore(self.soledad)

        attachment = yield store.get_mail_attachment(attachment_id)

        self.assertEqual({'content-type': 'foo/bar', 'content': bytearray('asdf')}, attachment)

    @defer.inlineCallbacks
    def test_store_attachment(self):
        content = 'this is some attachment content'
        content_type = 'text/plain'
        cdoc_serialized = {'content_transfer_encoding': 'base64', 'lkf': [], 'content_disposition': 'attachment',
                           'ctype': '', 'raw': 'dGhpcyBpcyBzb21lIGF0dGFjaG1lbnQgY29udGVudA==',
                           'phash': '9863729729D2E2EE8E52F0A7115CE33AD18DDA4B58E49AE08DD092D1C8E699B0',
                           'content_type': 'text/plain', 'type': 'cnt', 'charset': None}

        store = LeapAttachmentStore(self.soledad)

        attachment_id = yield store.add_attachment(content, content_type)

        self.assertEqual('9863729729D2E2EE8E52F0A7115CE33AD18DDA4B58E49AE08DD092D1C8E699B0', attachment_id)

        verify(self.soledad).create_doc(cdoc_serialized, doc_id=attachment_id)

    @defer.inlineCallbacks
    def test_store_attachment_twice_does_not_cause_exception(self):
        attachment_id = '9863729729D2E2EE8E52F0A7115CE33AD18DDA4B58E49AE08DD092D1C8E699B0'
        content = 'this is some attachment content'
        content_type = 'text/plain'
        cdoc_serialized = {'content_transfer_encoding': 'base64', 'lkf': [], 'content_disposition': 'attachment',
                           'ctype': '', 'raw': 'dGhpcyBpcyBzb21lIGF0dGFjaG1lbnQgY29udGVudA==',
                           'phash': '9863729729D2E2EE8E52F0A7115CE33AD18DDA4B58E49AE08DD092D1C8E699B0',
                           'content_type': 'text/plain', 'type': 'cnt'}
        doc = SoledadDocument(json=json.dumps({'content_type': content_type, 'raw': content}))
        when(self.soledad).get_from_index('by-type-and-payloadhash', 'cnt', attachment_id).thenReturn(defer.succeed([doc]))

        store = LeapAttachmentStore(self.soledad)

        when(self.soledad).create_doc(cdoc_serialized, doc_id=attachment_id).thenRaise(l2db.errors.RevisionConflict())

        actual_attachment_id = yield store.add_attachment(content, content_type)

        self.assertEqual(attachment_id, actual_attachment_id)

    @defer.inlineCallbacks
    def test_get_mail_attachment_different_content_encodings(self):
        attachment_id = '1B0A9AAD9E153D24265395203C53884506ABA276394B9FEC02B214BF9E77E48E'
        encoding_examples = [('', 'asdf', 'asdf'),
                             ('base64', 'asdf', 'YXNkZg=='),
                             ('quoted-printable', 'äsdf', '=C3=A4sdf')]

        for transfer_encoding, data, encoded_data in encoding_examples:
            doc = SoledadDocument(json=json.dumps({'content_type': 'foo/bar', 'raw': encoded_data,
                                                   'content_transfer_encoding': transfer_encoding}))
            when(self.soledad).get_from_index('by-type-and-payloadhash', 'cnt', attachment_id).thenReturn(defer.succeed([doc]))
            store = LeapAttachmentStore(self.soledad)

            attachment = yield store.get_mail_attachment(attachment_id)

            self.assertEqual(bytearray(data), attachment['content'])

    @defer.inlineCallbacks
    def test_get_mail_attachment_throws_exception_if_attachment_does_not_exist(self):
        attachment_id = '1B0A9AAD9E153D24265395203C53884506ABA276394B9FEC02B214BF9E77E48E'
        when(self.soledad).get_from_index('by-type-and-payloadhash', 'cnt', attachment_id).thenReturn(defer.succeed([]))
        store = LeapAttachmentStore(self.soledad)
        try:
            yield store.get_mail_attachment(attachment_id)
            self.fail('ValueError exception expected')
        except ValueError:
            pass

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

    def _mock_get_soledad_doc(self, doc_id, doc):
        soledad_doc = SoledadDocument(doc_id, json=json.dumps(doc.serialize()))

        with patch('mockito.invocation.AnswerSelector', AnswerSelector):
            when(self.soledad).get_doc(doc_id).thenAnswer(lambda: defer.succeed(soledad_doc))

        self.doc_by_id[doc_id] = soledad_doc
