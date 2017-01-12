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

import os
import re
from twisted.trial import unittest
from mockito import verify, mock
from mockito.matchers import Matcher
from email import message_from_file
from pixelated.adapter.model.mail import InputMail
from pixelated.adapter.welcome_mail import add_welcome_mail


class TestWelcomeMail(unittest.TestCase):

    def test_add_welcome_mail(self):
        mail_store = mock()
        input_mail = self._get_welcome_mail()

        add_welcome_mail(mail_store, 'pt-BR')
        capture = WelcomeMailCapture()

        verify(mail_store).add_mail('INBOX', capture)
        capture.assert_mail(input_mail.raw)

    def _get_welcome_mail(self):
        current_path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(current_path,
                               '..',
                               '..',
                               'pixelated',
                               'assets',
                               'welcome.mail.pt-BR')) as mail_template_file:
            mail_template = message_from_file(mail_template_file)

        return InputMail.from_python_mail(mail_template)


class WelcomeMailCapture(Matcher):

    def matches(self, arg):
        self.value = arg
        return True

    def assert_mail(self, mail):
        captured_mail = self._format(self.value)
        expected_mail = self._format(mail)
        assert captured_mail == expected_mail

    def _format(self, mail):
        splitter = '\n'
        mail_lines = mail.split(splitter)
        mail_lines = self._remove_boundaries(mail_lines)
        return splitter.join(mail_lines)

    def _remove_boundaries(self, mail_lines):
        # boundary example --===============5031169581469213585==--
        boundary_regex = re.compile("^(.*)(\={15})(\w*)(\={2})(.*)$")
        boundaries = filter(boundary_regex.match, mail_lines)
        return [line for line in mail_lines if line not in boundaries]
