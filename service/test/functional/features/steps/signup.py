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

from behave import given, then, when

from common import (
    element_should_have_content,
    fill_by_css_selector,
    find_element_by_css_selector)


@given(u'a user is accessing the signup page')  # noqa
def step_impl(context):
    context.browser.get(context.signup_url)


@when(u'I enter username, password and password confirmation')  # noqa
def step_impl(context):
    fill_by_css_selector(context, '#srp_username', context.username)
    fill_by_css_selector(context, '#srp_password', 'password')
    fill_by_css_selector(context, '#srp_password_confirmation', 'password')


@when(u'I click on the signup button')  # noqa
def step_impl(context):
    find_element_by_css_selector(context, 'button[type=submit]').click()


@then(u'I should see the user control panel')  # noqa
def step_impl(context):
    element_should_have_content(context, 'h1', 'user control panel')
