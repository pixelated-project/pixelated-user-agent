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
from mailbox import mbox
from twisted.trial import unittest
import pkg_resources
import random
from mock import patch

from pixelated.support.mail_generator import MailGenerator


class MailGeneratorTest(unittest.TestCase):

    def test_generator(self):
        mail = """Content-Type: text/plain; charset="us-ascii"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\nSubject: Scott\'s Laws with a longer subject Scott\'s Laws\nTo: alice@domain.test\nFrom: bob@domain.test\nDate: Sun, 18 Oct 2015 21:45:13 -0000\nX-Tags: \nX-Leap-Encryption: true\nX-Leap-Signature: valid\n\nFirst Law: No matter what goes wrong, it will probably look right. Scott\'s Second Law: When an error has been detected and corrected, it will probably look right. Scott\'s Second Law: When an error has been found in error, it will probably look right. Scott\'s Second Law: When an error has been found in error, it will probably look right. Scott\'s Second Law: When an error has been found in error, it will be impossible to fit the original quantity back into the \n\n First Law: No matter what goes wrong, it will be impossible to fit the original quantity back into the \n\n Scott\'s Second Law: When an error has been found in error, it will be found to have been wrong in the first place. After the correction has been found in error, it will be impossible to fit the original quantity back into the \n\n Second Law: When an error"""
        receiver = 'alice'
        domain_name = 'domain.test'
        mbox_file = pkg_resources.resource_filename('test.unit.fixtures', 'mbox')
        mails = mbox(mbox_file)
        rnd = random.Random(0)

        with patch('pixelated.support.mail_generator.time.time') as time_mock:
            time_mock.return_value = 1446029232.636018

            gen = MailGenerator(receiver, domain_name, mails, rnd)

            result = gen.generate_mail()

            self.assertEqual(mail, result.as_string())
