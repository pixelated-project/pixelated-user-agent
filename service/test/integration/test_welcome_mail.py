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

from test.support.integration import SoledadTestBase
from pixelated.config.welcome_mail import check_welcome_mail


class TestWelcomeMail(SoledadTestBase):

    def test_that_a_fresh_INBOX_will_receive_a_welcome_mail_only_once(self):
        inbox = self.mailboxes.inbox()
        check_welcome_mail(inbox)  # adds a mail
        check_welcome_mail(inbox)  # should not repeat

        inbox_mails = self.get_mails_by_tag('inbox')
        self.assertEquals(1, len(inbox_mails))

        self.delete_mail(inbox_mails[0].ident)
        check_welcome_mail(inbox)  # it is empty, but not fresh anymore

        inbox_mails = self.get_mails_by_tag('inbox')
        self.assertEquals(0, len(inbox_mails))
