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
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from test.support.integration import SoledadTestBase, load_mail_from_file
from twisted.internet import defer
import time
from contextlib import contextmanager


@contextmanager
def measure():
    start_time = time.time()
    start_clock = time.clock()
    yield
    end_time = time.time()
    end_clock = time.clock()
    # print 'time:  %10d - %10d = %10d' % (start_time, end_time, start_time - end_time)
    # print 'clock: %10d - %10d = %10d' % (start_clock, end_clock, start_clock - end_clock)


class LeapMailStoreTest(SoledadTestBase):

    @defer.inlineCallbacks
    def setUp(self):
        yield super(LeapMailStoreTest, self).setUp()

    @defer.inlineCallbacks
    def test_get_mail_for_measuring(self):
        self.maxDiff = None
        mail = load_mail_from_file('mbox00000000')
        mail_id = yield self._create_mail_in_soledad(mail)
        expected_mail_dict = {'body': u'Dignissimos ducimus veritatis. Est tenetur consequatur quia occaecati. Vel sit sit voluptas.\n\nEarum distinctio eos. Accusantium qui sint ut quia assumenda. Facere dignissimos inventore autem sit amet. Pariatur voluptatem sint est.\n\nUt recusandae praesentium aspernatur. Exercitationem amet placeat deserunt quae consequatur eum. Unde doloremque suscipit quia.\n\n', 'header': {u'date': u'Tue, 21 Apr 2015 08:43:27 +0000 (UTC)', u'to': [u'carmel@murazikortiz.name'], u'x-tw-pixelated-tags': u'nite, macro, trash', u'from': u'darby.senger@zemlak.biz', u'subject': u'Itaque consequatur repellendus provident sunt quia.'}, 'ident': mail_id, 'status': [], 'tags': set([]), 'textPlainBody': u'Dignissimos ducimus veritatis. Est tenetur consequatur quia occaecati. Vel sit sit voluptas.\n\nEarum distinctio eos. Accusantium qui sint ut quia assumenda. Facere dignissimos inventore autem sit amet. Pariatur voluptatem sint est.\n\nUt recusandae praesentium aspernatur. Exercitationem amet placeat deserunt quae consequatur eum. Unde doloremque suscipit quia.\n\n', 'mailbox': u'inbox', 'attachments': [], 'security_casing': {'imprints': [{'state': 'no_signature_information'}], 'locks': []}}

        with measure():
            result = yield self.app_test_client.mail_store.get_mail(mail_id, include_body=True)
        self.assertIsNotNone(result)
        self.assertEqual(expected_mail_dict, result.as_dict())

    @defer.inlineCallbacks
    def test_get_mail_with_body(self):
        self.maxDiff = None
        mail = load_mail_from_file('mbox00000000')
        mail_id = yield self._create_mail_in_soledad(mail)
        expected_mail_dict = {'body': u'Dignissimos ducimus veritatis. Est tenetur consequatur quia occaecati. Vel sit sit voluptas.\n\nEarum distinctio eos. Accusantium qui sint ut quia assumenda. Facere dignissimos inventore autem sit amet. Pariatur voluptatem sint est.\n\nUt recusandae praesentium aspernatur. Exercitationem amet placeat deserunt quae consequatur eum. Unde doloremque suscipit quia.\n\n', 'header': {u'date': u'Tue, 21 Apr 2015 08:43:27 +0000 (UTC)', u'to': [u'carmel@murazikortiz.name'], u'x-tw-pixelated-tags': u'nite, macro, trash', u'from': u'darby.senger@zemlak.biz', u'subject': u'Itaque consequatur repellendus provident sunt quia.'}, 'ident': mail_id, 'status': [], 'tags': set([]), 'textPlainBody': u'Dignissimos ducimus veritatis. Est tenetur consequatur quia occaecati. Vel sit sit voluptas.\n\nEarum distinctio eos. Accusantium qui sint ut quia assumenda. Facere dignissimos inventore autem sit amet. Pariatur voluptatem sint est.\n\nUt recusandae praesentium aspernatur. Exercitationem amet placeat deserunt quae consequatur eum. Unde doloremque suscipit quia.\n\n', 'mailbox': u'inbox', 'attachments': [], 'security_casing': {'imprints': [{'state': 'no_signature_information'}], 'locks': []}}

        result = yield self.app_test_client.mail_store.get_mail(mail_id, include_body=True)
        self.assertIsNotNone(result)
        self.assertEqual(expected_mail_dict, result.as_dict())

    @defer.inlineCallbacks
    def test_get_mail_with_attachment(self):
        input_mail = MIMEMultipart()
        input_mail.attach(MIMEText(u'a utf8 message', _charset='utf-8'))
        attachment = MIMEApplication('pretend to be binary attachment data')
        attachment.add_header('Content-Disposition', 'attachment', filename='filename.txt')
        input_mail.attach(attachment)

        mail = yield self.app_test_client.mail_store.add_mail('INBOX', input_mail.as_string())
        fetched_mail = yield self.app_test_client.mail_store.get_mail(mail.ident, include_body=True)
        self.assertTrue(fetched_mail.as_dict()['attachments'])

    @defer.inlineCallbacks
    def test_attachment_name(self):
        input_mail = MIMEMultipart()
        input_mail.attach(MIMEText(u'a utf8 message', _charset='utf-8'))
        attachment = MIMEApplication('pretend to be binary attachment data')
        attachment.add_header('Content-Disposition', 'attachment', filename='filename.txt')
        input_mail.attach(attachment)

        mail = yield self.app_test_client.mail_store.add_mail('INBOX', input_mail.as_string())
        fetched_mail = yield self.app_test_client.mail_store.get_mail(mail.ident, include_body=True)
        fetched_attachment_name = fetched_mail.as_dict()['attachments'][0]['name']
        self.assertEqual(fetched_attachment_name, 'filename.txt')

    @defer.inlineCallbacks
    def test_attachment_name_with_lowercase_header(self):
        input_mail = MIMEMultipart()
        input_mail.attach(MIMEText(u'a utf8 message', _charset='utf-8'))
        attachment = MIMEApplication('pretend to be binary attachment data')
        attachment.add_header('content-disposition', 'attachment', filename='filename.txt')
        input_mail.attach(attachment)

        mail = yield self.app_test_client.mail_store.add_mail('INBOX', input_mail.as_string())
        fetched_mail = yield self.app_test_client.mail_store.get_mail(mail.ident, include_body=True)
        fetched_attachment_name = fetched_mail.as_dict()['attachments'][0]['name']
        self.assertEqual(fetched_attachment_name, 'filename.txt')

    @defer.inlineCallbacks
    def test_round_trip_through_soledad_does_not_modify_content(self):
        mail = load_mail_from_file('mbox00000000')
        mail_id = yield self._create_mail_in_soledad(mail)
        expected_mail_dict = {'body': u'Dignissimos ducimus veritatis. Est tenetur consequatur quia occaecati. Vel sit sit voluptas.\n\nEarum distinctio eos. Accusantium qui sint ut quia assumenda. Facere dignissimos inventore autem sit amet. Pariatur voluptatem sint est.\n\nUt recusandae praesentium aspernatur. Exercitationem amet placeat deserunt quae consequatur eum. Unde doloremque suscipit quia.\n\n', 'header': {u'date': u'Tue, 21 Apr 2015 08:43:27 +0000 (UTC)', u'to': [u'carmel@murazikortiz.name'], u'x-tw-pixelated-tags': u'nite, macro, trash', u'from': u'darby.senger@zemlak.biz', u'subject': u'Itaque consequatur repellendus provident sunt quia.'}, 'ident': mail_id, 'status': [], 'tags': set([])}

        mail = yield self.app_test_client.mail_store.add_mail('INBOX', mail.as_string())
        fetched_mail = yield self.app_test_client.mail_store.get_mail(mail_id, include_body=True)
        self.assertEqual(expected_mail_dict['header'], mail.as_dict()['header'])
        self.assertEqual(expected_mail_dict['header'], fetched_mail.as_dict()['header'])

    @defer.inlineCallbacks
    def test_round_trip_through_soledad_keeps_attachment(self):
        input_mail = MIMEMultipart()
        input_mail.attach(MIMEText(u'a utf8 message', _charset='utf-8'))
        attachment = MIMEApplication('pretend to be binary attachment data')
        attachment.add_header('Content-Disposition', 'attachment', filename='filename.txt')
        input_mail.attach(attachment)

        mail = yield self.app_test_client.mail_store.add_mail('INBOX', input_mail.as_string())
        fetched_mail = yield self.app_test_client.mail_store.get_mail(mail.ident, include_body=True)
        self.assertDictEqual(mail.as_dict(), fetched_mail.as_dict())

    @defer.inlineCallbacks
    def test_all_mails(self):
        mail = load_mail_from_file('mbox00000000')
        yield self._create_mail_in_soledad(mail)

        mails = yield self.app_test_client.mail_store.all_mails()

        self.assertEqual(1, len(mails))
        self.assertEqual('Itaque consequatur repellendus provident sunt quia.', mails[0].subject)

    @defer.inlineCallbacks
    def test_add_and_remove_mail(self):
        yield self.adaptor.initialize_store(self.app_test_client.soledad)
        mail = load_mail_from_file('mbox00000000')
        yield self.app_test_client.mail_store.add_mailbox('INBOX')

        msg = yield self.app_test_client.mail_store.add_mail('INBOX', mail.as_string())

        yield self.app_test_client.mail_store.delete_mail(msg.mail_id)

        deleted_msg = yield self.app_test_client.mail_store.get_mail(msg.mail_id)

        self.assertIsNone(deleted_msg)

    @defer.inlineCallbacks
    def test_add_add_mail_twice(self):
        yield self.adaptor.initialize_store(self.app_test_client.soledad)
        mail = load_mail_from_file('mbox00000000', enforceUniqueMessageId=True)
        mail2 = load_mail_from_file('mbox00000000', enforceUniqueMessageId=True)
        yield self.app_test_client.mail_store.add_mailbox('INBOX')

        msg1 = yield self.app_test_client.mail_store.add_mail('INBOX', mail.as_string())
        msg2 = yield self.app_test_client.mail_store.add_mail('INBOX', mail2.as_string())

        self.assertIsNotNone(msg1.ident)
        self.assertIsNotNone(msg2.ident)

    @defer.inlineCallbacks
    def test_get_mailbox_mail_ids(self):
        mail = load_mail_from_file('mbox00000000')
        yield self.app_test_client.mail_store.add_mailbox('INBOX')
        mail = yield self.app_test_client.mail_store.add_mail('INBOX', mail.as_string())

        mails = yield self.app_test_client.mail_store.get_mailbox_mail_ids('INBOX')

        self.assertEqual(1, len(mails))
        self.assertEqual(mail.mail_id, mails[0])

    @defer.inlineCallbacks
    def test_deleting_a_deleted_mail_doesnt_raise_errors(self):
        mail = load_mail_from_file('mbox00000000')
        yield self.app_test_client.mail_store.add_mailbox('INBOX')
        mail = yield self.app_test_client.mail_store.add_mail('INBOX', mail.as_string())

        yield self.app_test_client.mail_store.delete_mail(mail.ident)
        try:
            yield self.app_test_client.mail_store.delete_mail(mail.ident)
        except Exception as e:
            self.fail("Deleting a deleted mail should be ok, but raised an error")
            raise e
