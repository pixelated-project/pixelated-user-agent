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
from mock import MagicMock

from pixelated.bitmask_libraries.session import LeapSession
from test_abstract_leap import AbstractLeapTest
from twisted.internet import defer


class SessionTest(AbstractLeapTest):

    def setUp(self):
        super(SessionTest, self).setUp()
        self.smtp_mock = MagicMock()

    def test_background_jobs_are_started_during_initial_sync(self):
        with patch('pixelated.bitmask_libraries.session.reactor.callFromThread', new=_execute_func) as _:
            with patch('pixelated.bitmask_libraries.session.LeapSession._create_incoming_mail_fetcher') as mail_fetcher_mock:
                session = self._create_session()
                yield session.initial_sync()
                mail_fetcher_mock.startService.assert_called_once_with()

    def test_that_close_stops_background_jobs(self):
        with patch('pixelated.bitmask_libraries.session.reactor.callFromThread', new=_execute_func) as _:
            with patch('pixelated.bitmask_libraries.session.LeapSession._create_incoming_mail_fetcher') as mail_fetcher_mock:
                session = self._create_session()
                yield session.initial_sync()
                session.close()
                mail_fetcher_mock.stopService.assert_called_once_with()

    def test_that_sync_deferes_to_soledad(self):
        session = self._create_session()

        session.sync()

        self.soledad_session.sync.assert_called_once_with()

    def _create_session(self):
        return LeapSession(self.provider, self.auth, self.mail_store, self.soledad_session, self.nicknym, self.smtp_mock)


def _execute_func(func):
    func()
