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
from crochet import wait_for


@given('I have a mail in my inbox')
def add_mail_impl(context):
    subject = 'Hi! This the subject %s' % uuid4()

    input_mail = MailBuilder().with_subject(subject).build_input_mail()

    load_mail_into_soledad(context, input_mail)
    wait_for_condition(context, lambda _: context.single_user_client.search_engine.search(subject)[1] > 0, poll_frequency=0.1)

    context.last_subject = subject


@given('I have a mail for {username} in my inbox')
def add_mail_to_user_inbox(context, username):
    subject = 'Hi! This the subject %s' % uuid4()

    input_mail = MailBuilder().with_subject(subject).build_input_mail()

    load_mail_into_user_account(context, input_mail, username)
    wait_for_condition(context, lambda _: context.multi_user_client.account_for(username).search_engine.search(subject)[1] > 0, poll_frequency=0.1)

    context.last_subject = subject


@given(u'Account for user {username} exists')
def add_account(context, username):
    add_multi_user_account(context, username)


@wait_for(timeout=10.0)
def load_mail_into_soledad(context, mail):
    return context.single_user_client.mail_store.add_mail('INBOX', mail.raw)


@wait_for(timeout=10.0)
def load_mail_into_user_account(context, mail, username):
    return context.multi_user_client.add_mail_to_user_inbox(mail, username)


@wait_for(timeout=10.0)
def add_multi_user_account(context, username):
    return context.multi_user_client.create_user('username')
