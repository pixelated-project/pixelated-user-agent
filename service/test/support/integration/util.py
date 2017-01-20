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
from email.parser import Parser
from email.utils import make_msgid
import os
import pkg_resources


def load_mail_from_file(mail_file, enforceUniqueMessageId=False):
    mailset_dir = pkg_resources.resource_filename(
        'test.unit.fixtures', 'mailset')
    mail_file = os.path.join(mailset_dir, 'new', mail_file)
    with open(mail_file) as f:
        mail = Parser().parse(f)

    if enforceUniqueMessageId:
        mail.add_header('Message-Id', make_msgid())

    return mail
