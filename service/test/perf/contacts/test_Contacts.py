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
import unittest

from funkload.FunkLoadTestCase import FunkLoadTestCase
from test.support.integration import AppTestClient
from test.support.dispatcher.proxy import Proxy
from crochet import setup, wait_for
from leap.common.events.server import ensure_server
setup()


@wait_for(timeout=5.0)
def start_app_test_client(client):
    ensure_server()
    return client.start_client()


class Contacts(FunkLoadTestCase):

    def setUpBench(self):
        client = AppTestClient()
        start_app_test_client(client)
        client.listenTCP()
        proxy = Proxy(proxy_port='8889', app_port='4567')

        # setup data
        client.add_multiple_to_mailbox(10, 'INBOX', to='to@inbox.com', cc='cc@inbox.com', bcc='bcc@inbox.com')
        client.add_multiple_to_mailbox(10, 'TRASH', to='to@trash.com', cc='cc@trash.com', bcc='bcc@trash.com')
        client.add_multiple_to_mailbox(10, 'DRAFTS', to='to@drafts.com', cc='cc@drafts.com', bcc='bcc@drafts.com')

        self.call_to_terminate = proxy.run_on_a_thread()

    def tearDownBench(self):
        self.call_to_terminate()

    def setUp(self):
        """Setting up test."""
        self.server_url = self.conf_get('main', 'url')

    def test_contacts(self):
        server_url = self.server_url
        nb_time = self.conf_getInt('main', 'nb_time')

        for i in range(nb_time):
            self.get(server_url, description='Get Contacts')

if __name__ in ('main', '__main__'):
    unittest.main()
