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

from behave import then, when
from selenium.webdriver.common.keys import Keys

from common import (
    click_button,
    find_element_by_css_selector,
    find_elements_by_css_selector,
    reply_subject,
    wait_until_button_is_visible)


@then('I see that the subject reads \'{subject}\'')
def impl(context, subject):
    e = find_element_by_css_selector(context, '#mail-view .mail-read-view__header-subject')
    assert e.text == subject


@then('I see that the body reads \'{expected_body}\'')
def impl(context, expected_body):
    find_element_by_css_selector(context, '#read-sandbox')
    context.browser.switch_to_frame('read-sandbox')
    e = find_element_by_css_selector(context, 'body')
    assert e.text == expected_body
    context.browser.switch_to_default_content()


@then('that email has the \'{tag}\' tag')
def impl(context, tag):
    find_element_by_css_selector(context, '#mail-view .tagsArea .tag')
    elements = find_elements_by_css_selector(context, '#mail-view .tagsArea .tag')
    tags = [e.text for e in elements]
    assert tag in tags


@when('I add the tag \'{tag}\' to that mail')
def impl(context, tag):
    b = find_element_by_css_selector(context, '#new-tag-button')
    b.click()

    e = find_element_by_css_selector(context, '#new-tag-input')
    e.send_keys(tag)
    e.send_keys(Keys.ENTER)
    find_element_by_css_selector(context, 'li[data-tag=%s]' % tag)


@when('I reply to it')
def impl(context):
    click_button(context, 'Reply')
    context.reply_subject = reply_subject(context)
    click_button(context, 'Send')


@when('I try to delete the first mail')
def impl(context):
    context.execute_steps(u"When I open the first mail in the mail list")
    find_element_by_css_selector(context, '#mail-view #view-more-actions').click()
    context.browser.execute_script("$('#delete-button-top').click();")

    e = find_element_by_css_selector(context, '.message-panel__growl--success')
    assert 'Your message was moved to trash!' == e.text


@when('I choose to forward this mail')
def impl(context):
    wait_until_button_is_visible(context, 'Forward')
    click_button(context, 'Forward')


@when('I forward this mail')
def impl(context):
    wait_until_button_is_visible(context, 'Send')
    click_button(context, 'Send')


@when('I remove all tags')
def impl(context):
    e = find_element_by_css_selector(context, '.tagsArea')
    tags = e.find_elements_by_css_selector('.tag')
    assert len(tags) > 0
    for tag in tags:
        tag.click()


@when('I choose to trash')
def impl(context):
    context.browser.execute_script("$('button#view-more-actions').click()")
    click_button(context, 'Delete this message', 'li')


@then('I see the mail has a cc and a bcc recipient')
def impl(context):
    cc = find_element_by_css_selector(context, '.mail-read-view__header-recipients .cc')
    bcc = find_element_by_css_selector(context, '.mail-read-view__header-recipients .bcc')

    assert cc is not None
    assert bcc is not None
