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

import time

from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

TIMEOUT_IN_S = 20

DEFAULT_IMPLICIT_WAIT_TIMEOUT_IN_S = 10.0


class ImplicitWait(object):
    def __init__(self, context, timeout=5.0):
        self._context = context
        self._timeout = timeout

    def __enter__(self):
        self._context.browser.implicitly_wait(self._timeout)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._context.browser.implicitly_wait(DEFAULT_IMPLICIT_WAIT_TIMEOUT_IN_S)


def wait_until_element_is_invisible_by_locator(context, locator_tuple, timeout=TIMEOUT_IN_S):
    wait = WebDriverWait(context.browser, timeout)
    wait.until(EC.invisibility_of_element_located(locator_tuple))


def wait_for_loading_to_finish(context, timeout=TIMEOUT_IN_S):
    wait_until_element_is_invisible_by_locator(context, (By.ID, 'loading'), timeout)


def wait_for_user_alert_to_disapear(context, timeout=TIMEOUT_IN_S):
    wait_until_element_is_invisible_by_locator(context, (By.ID, 'user-alerts'), timeout)


def _wait_until_elements_are_visible_by_locator(context, locator_tuple, timeout=TIMEOUT_IN_S):
    wait = WebDriverWait(context.browser, timeout)
    wait.until(EC.presence_of_all_elements_located(locator_tuple))
    return context.browser.find_elements(locator_tuple[0], locator_tuple[1])


def _wait_until_element_is_visible_by_locator(context, locator_tuple, timeout=TIMEOUT_IN_S):
    wait = WebDriverWait(context.browser, timeout)
    wait.until(EC.presence_of_element_located(locator_tuple))
    return context.browser.find_element(locator_tuple[0], locator_tuple[1])


def wait_for_condition(context, predicate_func, timeout=TIMEOUT_IN_S, poll_frequency=0.1):
    wait = WebDriverWait(context.browser, timeout, poll_frequency=poll_frequency)
    wait.until(predicate_func)


def fill_by_xpath(context, xpath, text):
    field = context.browser.find_element_by_xpath(xpath)
    field.send_keys(text)


def fill_by_css_selector(context, css_selector, text, timeout=TIMEOUT_IN_S):
    field = find_element_by_css_selector(context, css_selector, timeout=timeout)
    field.send_keys(text)


def take_screenshot(context, filename):
    context.browser.save_screenshot(filename)


def page_has_css(context, css):
    try:
        find_element_by_css_selector(context, css)
        return True
    except TimeoutException:
        return False


def find_element_by_xpath(context, xpath):
    return _wait_until_element_is_visible_by_locator(context, (By.XPATH, xpath))


def find_element_by_id(context, id):
    return _wait_until_element_is_visible_by_locator(context, (By.ID, id))


def find_element_by_css_selector(context, css_selector, timeout=TIMEOUT_IN_S):
    return _wait_until_element_is_visible_by_locator(context, (By.CSS_SELECTOR, css_selector), timeout=timeout)


def find_element_by_class_name(context, class_name):
    return _wait_until_element_is_visible_by_locator(context, (By.CLASS_NAME, class_name))


def find_elements_by_css_selector(context, css_selector, timeout=TIMEOUT_IN_S):
    return _wait_until_elements_are_visible_by_locator(context, (By.CSS_SELECTOR, css_selector), timeout=timeout)


def find_elements_by_xpath(context, xpath, timeout=TIMEOUT_IN_S):
    return _wait_until_elements_are_visible_by_locator(context, (By.XPATH, xpath), timeout=timeout)


def find_element_containing_text(context, text, element_type='*'):
    return find_element_by_xpath(context, "//%s[contains(.,'%s')]" % (element_type, text))


def element_should_have_content(context, css_selector, content):
    e = find_element_by_css_selector(context, css_selector)
    assert e.text == content


def wait_until_button_is_visible(context, title, timeout=TIMEOUT_IN_S):
    wait = WebDriverWait(context.browser, timeout)
    locator_tuple = (By.XPATH, ("//%s[contains(.,'%s')]" % ('button', title)))
    wait.until(EC.visibility_of_element_located(locator_tuple))


def execute_ignoring_staleness(func, timeout=TIMEOUT_IN_S):
    end_time = time.time() + timeout
    while time.time() <= end_time:
        try:
            return func()
        except StaleElementReferenceException:
            pass
    raise TimeoutException('did not solve stale state until timeout %f' % timeout)


def click_button(context, title, element='button'):
    button = find_element_containing_text(context, title, element_type=element)
    button.click()


def mail_list_with_subject_exists(context, subject):
    return find_element_by_xpath(context, "//*[@class='mail-list-entry__item-subject' and contains(.,'%s')]" % subject)


def reply_subject(context):
    e = find_element_by_css_selector(context, '#reply-subject')
    return e.text
