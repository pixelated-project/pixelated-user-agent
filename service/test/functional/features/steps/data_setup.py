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
from test.support.integration import MailBuilder
from behave import given
from common import wait_for_condition


@given('I have a mail in my inbox')
def add_mail_impl(context):
    subject = 'Hi! This the subject %s' % uuid4()

    input_mail = MailBuilder().with_subject(subject).build_input_mail()
    context.client.add_mail_to_inbox(input_mail)

    wait_for_condition(context, lambda _: context.client.search_engine.search(subject)[1] > 0, poll_frequency=0.1)

    context.last_subject = subject
