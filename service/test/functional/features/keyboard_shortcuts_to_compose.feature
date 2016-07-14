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

@wip
Feature: Using keyboard shortcuts to compose and send a mail
  As a user of pixelated
  I want to use keyboard shortcuts
  So I can compose mails

  Scenario: User composes a mail and sends it using shortcuts
    When I use a shortcut to compose a message with
      | subject          | body                                        |
      | Pixelated rocks! | You should definitely use it. Cheers, User. |
    And for the 'To' field I enter 'pixelated@friends.org'
    And I use a shortcut to send it
    When I select the tag 'sent'
    And I open the first mail in the mail list
    Then I see that the subject reads 'Pixelated rocks!'
    Then I see that the body reads 'You should definitely use it. Cheers, User.'

