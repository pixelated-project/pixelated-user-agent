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
from common import *
from selenium.common.exceptions import NoSuchElementException


def find_current_mail(context):
    print 'searching for mail [%s]' % context.current_mail_id
    return find_element_by_id(context, '%s' % context.current_mail_id)


def check_current_mail_is_visible(context):
    find_current_mail(context)


def open_current_mail(context):
    e = find_current_mail(context)
    e.click()


def get_first_email(context):
    return wait_until_elements_are_visible_by_locator(context, (By.CSS_SELECTOR, '#mail-list li span a'))[0]


@then('I see that mail under the \'{tag}\' tag')
def impl(context, tag):
    context.execute_steps("when I select the tag '%s'" % tag)
    context.execute_steps(u'When I open the first mail in the mail list')


@when('I open that mail')
def impl(context):
    find_current_mail(context).click()


@when('I open the first mail in the mail list')
def impl(context):
    # it seems page is often still loading so staleness exceptions happen often
    context.current_mail_id = 'mail-' + execute_ignoring_staleness(lambda: get_first_email(context).get_attribute('href').split('/')[-1])
    execute_ignoring_staleness(lambda: get_first_email(context).click())


@when('I open the first mail in the \'{tag}\'')
def impl(context, tag):
    context.execute_steps(u"When I select the tag '%s'" % tag)
    context.execute_steps(u'When I open the first mail in the mail list')


@when('I open the mail I previously tagged')
def impl(context):
    open_current_mail(context)


@then('I see the mail I sent')
def impl(context):
    src = context.browser.page_source
    assert context.reply_subject in src


@then('the deleted mail is there')
def impl(context):
    mail_list_with_subject_exists(context, context.last_subject)


@given('I have mails')
def impl(context):
    emails = wait_until_elements_are_visible_by_locator(context, (By.CSS_SELECTOR, '#mail-list li span a'))
    assert len(emails) > 0


@when('I mark the first unread email as read')
def impl(context):
    emails = wait_until_elements_are_visible_by_locator(context, (By.CSS_SELECTOR, '#mail-list li'))

    for email in emails:
        if 'status-read' not in email.get_attribute('class'):
            context.current_mail_id = email.get_attribute('id')  # we need to get the mail id before manipulating the page
            email.find_element_by_tag_name('input').click()
            find_element_by_id(context, 'mark-selected-as-read').click()
            break
    wait_until_elements_are_visible_by_locator(context, (By.CSS_SELECTOR, '#%s.status-read' % context.current_mail_id))


@when('I delete the email')
def impl(context):
    def last_email():
        return wait_until_element_is_visible_by_locator(context, (By.CSS_SELECTOR, '#mail-list li'))
    mail = last_email()
    context.current_mail_id = mail.get_attribute('id')
    mail.find_element_by_tag_name('input').click()
    find_element_by_id(context, 'delete-selected').click()
    _wait_for_mail_list_to_be_empty(context)


def _wait_for_mail_list_to_be_empty(context):
    wait_for_loading_to_finish(context)

    def mail_list_is_empty(_):
        with ImplicitWait(context, timeout=0.1):
            try:
                return 0 == len(context.browser.find_elements_by_css_selector('#mail-list li'))
            except TimeoutException:
                return False

    wait_for_condition(context, mail_list_is_empty)


@when('I check all emails')
def impl(context):
    find_element_by_id(context, 'toggle-check-all-emails').click()


@when('I delete them permanently')
def impl(context):
    find_element_by_id(context, 'delete-selected').click()


@then('I should not see any email')
def impl(context):
    _wait_for_mail_list_to_be_empty(context)
