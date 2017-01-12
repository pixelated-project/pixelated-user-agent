#
# Copyright (c) 2016 ThoughtWorks, Inc.
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

@smoke
Feature: sign up, login and logout
  As a visitor of Pixelated
  I want to sign up
  So I can log in to my account and see the welcome email

  Scenario: Visitor creates his account
    Given a user is accessing the signup page
    When I enter username, password and password confirmation
    And I click on the signup button
    Then I should see the user control panel

  Scenario: Existing user logs into his account
    Given a user is accessing the login page
    When I enter username and password as credentials
    And I click on the login button
    Then I should see the fancy interstitial
    Then I have mails
    When I logout
    Then I should see the login page
