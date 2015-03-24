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

from pixelated.config.welcome_mail import build_welcome_mail
from pixelated.adapter.model.mail import InputMail


class WelcomeMailTest(unittest.TestCase):

    def test_build_plain_welcome_mail(self):
        user_address = InputMail.FROM_EMAIL_ADDRESS = 'welcomed@user'
        mail = build_welcome_mail()
        self.assertEquals(user_address, mail.to)
        self.assertEquals('Welcome to Pixelated Mail', mail.headers['Subject'])
        self.assertIn('How to use it', mail.body)
        self.assertIn('text/plain', mail._mime.as_string())
        self.assertIn('text/html', mail._mime.as_string())
        self.assertTrue(mail.headers['Date'])
