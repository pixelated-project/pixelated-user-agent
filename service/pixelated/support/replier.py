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

from email.utils import parseaddr


def generate_recipients(sender, to, ccs, current_user):
    result = {'single': None, 'all': {'to-field': [], 'cc-field': []}}

    to.append(sender)
    to = remove_duplicates(to)
    ccs = remove_duplicates(ccs)

    result['single'] = swap_recipient_if_needed(sender, remove_address(to, current_user), current_user)
    result['all']['to-field'] = remove_address(to, current_user) if len(to) > 1 else to
    result['all']['cc-field'] = remove_address(ccs, current_user) if len(ccs) > 1 else ccs
    return result


def remove_duplicates(recipients):
    return list(set(recipients))


def remove_address(recipients, current_user):
    return [recipient for recipient in recipients if not parsed_mail_matches(recipient, current_user)]


def parsed_mail_matches(to_parse, expected):
    return parseaddr(to_parse)[1] == expected


def swap_recipient_if_needed(sender, recipients, current_user):
    if len(recipients) == 1 and parsed_mail_matches(sender, current_user):
        return recipients[0]
    return sender
