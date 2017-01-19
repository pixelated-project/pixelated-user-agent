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

import os
import requests


class FeedbackService(object):
    FEEDBACK_URL = os.environ.get('FEEDBACK_URL')

    def __init__(self, leap_session):
        self.leap_session = leap_session

    def open_ticket(self, feedback):
        account_mail = self.leap_session.account_email()
        data = {
            "ticket[comments_attributes][0][body]": feedback,
            "ticket[subject]": "Feedback user-agent from {0}".format(account_mail),
            "ticket[email]": account_mail,
            "ticket[regarding_user]": account_mail
        }

        return requests.post(self.FEEDBACK_URL, data=data, verify=False)
