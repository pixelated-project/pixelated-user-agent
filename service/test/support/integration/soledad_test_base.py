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
from uuid import uuid4
from leap.bitmask.mail.adaptors.soledad import SoledadMailAdaptor
from leap.bitmask.mail.mail import Message
from twisted.internet import defer
from twisted.trial import unittest
from test.support.integration.app_test_client import AppTestClient
from test.support.integration.multi_user_client import MultiUserClient
from leap.common.events.flags import set_events_enabled


class SoledadTestBase(unittest.TestCase):
    Client = AppTestClient
    # these are so long because our CI is so slow at the moment.
    DEFERRED_TIMEOUT = 120
    DEFERRED_TIMEOUT_LONG = 300

    @defer.inlineCallbacks
    def setUp(self):
        set_events_enabled(False)
        super(SoledadTestBase, self).setUp()
        self.adaptor = SoledadMailAdaptor()
        self.mbox_uuid = str(uuid4())
        yield self.app_test_client.start_client()

    def tearDown(self):
        set_events_enabled(True)
        self.app_test_client.cleanup()

    @property
    def app_test_client(self):
        if not hasattr(self, '_app_test_client'):
            self._app_test_client = self.Client()
        return self._app_test_client

    @defer.inlineCallbacks
    def _create_mail_in_soledad(self, mail):
        yield self.adaptor.initialize_store(self.app_test_client.soledad)
        mbox = yield self.adaptor.get_or_create_mbox(self.app_test_client.soledad, 'INBOX')
        message = self._convert_mail_to_leap_message(mail, mbox.uuid)
        yield self.adaptor.create_msg(self.app_test_client.soledad, message)

        defer.returnValue(message.get_wrapper().mdoc.doc_id)

    def _convert_mail_to_leap_message(self, mail, mbox_uuid):
        message = self.adaptor.get_msg_from_string(Message, mail.as_string())
        message.get_wrapper().set_mbox_uuid(mbox_uuid)
        return message


class MultiUserSoledadTestBase(SoledadTestBase):
    Client = MultiUserClient
