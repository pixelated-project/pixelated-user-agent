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
from mock import patch

from twisted.internet import defer

from test.support.integration import load_mail_from_file
from test.support.integration.soledad_test_base import MultiUserSoledadTestBase


class MultiUserLoginTest(MultiUserSoledadTestBase):

    @defer.inlineCallbacks
    def test_logged_out_users_should_receive_unauthorized(self):
        response, request = yield self.app_test_client.get("/mail", as_json=False)

        response_str = yield response
        self.assertEqual(401, request.responseCode)
        self.assertEquals('Unauthorized!', response_str)

    @defer.inlineCallbacks
    def test_logged_in_users_sees_resources(self):
        response, login_request = yield self.app_test_client.login()
        yield response

        mail = load_mail_from_file('mbox00000000')
        mail_id = yield self._create_mail_in_soledad(mail)
        expected_mail_dict = {'body': u'Dignissimos ducimus veritatis. Est tenetur consequatur quia occaecati. Vel sit sit voluptas.\n\nEarum distinctio eos. Accusantium qui sint ut quia assumenda. Facere dignissimos inventore autem sit amet. Pariatur voluptatem sint est.\n\nUt recusandae praesentium aspernatur. Exercitationem amet placeat deserunt quae consequatur eum. Unde doloremque suscipit quia.\n\n', 'header': {u'date': u'Tue, 21 Apr 2015 08:43:27 +0000 (UTC)', u'to': [u'carmel@murazikortiz.name'], u'x-tw-pixelated-tags': u'nite, macro, trash', u'from': u'darby.senger@zemlak.biz', u'subject': u'Itaque consequatur repellendus provident sunt quia.'}, 'ident': mail_id, 'status': [], 'tags': [], 'textPlainBody': u'Dignissimos ducimus veritatis. Est tenetur consequatur quia occaecati. Vel sit sit voluptas.\n\nEarum distinctio eos. Accusantium qui sint ut quia assumenda. Facere dignissimos inventore autem sit amet. Pariatur voluptatem sint est.\n\nUt recusandae praesentium aspernatur. Exercitationem amet placeat deserunt quae consequatur eum. Unde doloremque suscipit quia.\n\n', 'mailbox': u'inbox', 'attachments': [], 'security_casing': {'imprints': [{'state': 'no_signature_information'}], 'locks': []}}
        response, request = self.app_test_client.get("/mail/%s" % mail_id, from_request=login_request)
        response = yield response

        self.assertEqual(200, request.code)
        for key, val in expected_mail_dict.items():
            self.assertEquals(val, response[key])

    @defer.inlineCallbacks
    def test_wrong_credentials_cannot_access_resources(self):
        response, login_request = self.app_test_client.login('username', 'wrong_password')
        response_str = yield response
        self.assertEqual(401, login_request.responseCode)
        self.assertIn('Invalid username or password', login_request.written)
