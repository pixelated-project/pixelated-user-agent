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

from behave import when, then
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from common import find_element_by_css_selector, find_elements_by_css_selector


@when('I search for a mail with the words "{search_term}"')
def impl(context, search_term):
    search_field = find_element_by_css_selector(context, '#search-trigger input[type="search"]')
    ActionChains(context.browser)\
        .send_keys_to_element(search_field, search_term)\
        .send_keys_to_element(search_field, Keys.ENTER)\
        .perform()


@then('I see one or more mails in the search results')
def impl(context):
    lis = find_elements_by_css_selector(context, '#mail-list li')
    assert len(lis) >= 1
