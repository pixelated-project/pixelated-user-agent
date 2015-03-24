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
from pixelated.adapter.model.mail import InputMail
from pixelated.support.date import iso_now
from email import message_from_file
from email.MIMEMultipart import MIMEMultipart


def check_welcome_mail(mailbox):
    if mailbox.fresh:
        welcome_mail = build_welcome_mail()
        mailbox.add(welcome_mail)


def build_welcome_mail():
    current_path = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_path, '..', 'assets', 'welcome.mail')) as mail_template_file:
        mail_template = message_from_file(mail_template_file)
    welcome_mail = InputMail()
    welcome_mail.headers['To'] = InputMail.FROM_EMAIL_ADDRESS
    welcome_mail.headers['Subject'] = mail_template['Subject']
    welcome_mail.headers['Date'] = iso_now()
    welcome_mail._mime = MIMEMultipart()
    for payload in mail_template.get_payload():
        welcome_mail._mime.attach(payload)
        if payload.get_content_type() == 'text/plain':
            welcome_mail.body = payload.as_string()
    return welcome_mail


def check_welcome_mail_wrapper(mailbox):
    def wrapper(*args, **kwargs):
        check_welcome_mail(mailbox)
    return wrapper
