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
from behave import when
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep

from common import *


@when('I compose a message with')
def impl(context):
    toggle = context.browser.find_element_by_id('compose-mails-trigger')
    toggle.click()

    for row in context.table:
        fill_by_css_selector(context, 'input#subject', row['subject'])
        fill_by_css_selector(context, 'textarea#text-box', row['body'])


@when('I use a shortcut to compose a message with')
def compose_with_shortcut(context):
    body = context.browser.find_element_by_tag_name('body')
    body.send_keys('c')

    for row in context.table:
        fill_by_css_selector(context, 'input#subject', row['subject'])
        fill_by_css_selector(context, 'textarea#text-box', row['body'])


@when("for the '{recipients_field}' field I enter '{to_type}'")
def enter_address_impl(context, recipients_field, to_type):
    _enter_recipient(context, recipients_field, to_type + "\n")


@when("for the '{recipients_field}' field I type '{to_type}' and chose the first contact that shows")
def choose_impl(context, recipients_field, to_type):
    _enter_recipient(context, recipients_field, to_type)
    sleep(1)
    find_element_by_css_selector(context, '.tt-dropdown-menu div div').click()


@when('I send it')
def send_impl(context):
    send_button = wait_until_element_is_visible_by_locator(context, (By.CSS_SELECTOR, '#send-button:enabled'))
    send_button.click()


@when('I use a shortcut to send it')
def send_with_shortcut(context):
    ActionChains(context.browser).key_down(Keys.CONTROL).send_keys(Keys.ENTER).key_up(Keys.CONTROL).perform()


@when(u'I toggle the cc and bcc fields')
def collapse_cc_bcc_fields(context):
    cc_and_bcc_chevron = wait_until_element_is_visible_by_locator(context, (By.CSS_SELECTOR, '#cc-bcc-collapse'))
    cc_and_bcc_chevron.click()


def _enter_recipient(context, recipients_field, to_type):
    recipients_field = recipients_field.lower()
    browser = context.browser
    field = browser.find_element_by_css_selector('#recipients-%s-area .tt-input' % recipients_field)
    field.send_keys(to_type)
