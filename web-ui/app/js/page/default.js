/*
 * Copyright (c) 2014 ThoughtWorks, Inc.
 *
 * Pixelated is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Pixelated is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with Pixelated. If not, see <http://www.gnu.org/licenses/>.
 */
define(
  [
    'mail_view/ui/compose_box',
    'mail_list_actions/ui/mail_list_actions',
    'user_alerts/ui/user_alerts',
    'mail_list/ui/mail_list',
    'mail_view/ui/no_message_selected_pane',
    'mail_view/ui/no_mails_available_pane',
    'mail_view/ui/mail_view',
    'mail_view/ui/mail_actions',
    'mail_view/ui/reply_section',
    'mail_view/data/mail_sender',
    'services/mail_service',
    'services/delete_service',
    'services/recover_service',
    'tags/ui/tag_list',
    'tags/data/tags',
    'page/router',
    'dispatchers/right_pane_dispatcher',
    'dispatchers/middle_pane_dispatcher',
    'dispatchers/left_pane_dispatcher',
    'search/search_trigger',
    'search/results_highlighter',
    'foundation/off_canvas',
    'page/pane_contract_expand',
    'views/i18n',
    'views/recipientListFormatter',
    'flight/lib/logger',
    'page/user_settings_icon',
    'page/user_settings_box',
    'page/logout',
    'page/logout_shortcut',
    'feedback/feedback_trigger',
    'mail_view/ui/feedback_box',
    'mail_view/data/feedback_sender',
    'page/version',
  ],

  function (
    composeBox,
    mailListActions,
    userAlerts,
    mailList,
    noMessageSelectedPane,
    noMailsAvailablePane,
    mailView,
    mailViewActions,
    replyButton,
    mailSender,
    mailService,
    deleteService,
    recoverService,
    tagList,
    tags,
    router,
    rightPaneDispatcher,
    middlePaneDispatcher,
    leftPaneDispatcher,
    searchTrigger,
    resultsHighlighter,
    offCanvas,
    paneContractExpand,
    viewI18n,
    recipientListFormatter,
    withLogging,
    userSettingsIcon,
    userSettingsBox,
    logout,
    logoutShortcut,
    feedback,
    feedbackBox,
    feedbackSender,
    version) {

    'use strict';
    function initialize(path) {
      viewI18n.init(path + '/assets/');
      paneContractExpand.attachTo(document);

      userAlerts.attachTo('#user-alerts');

      mailList.attachTo('#mail-list');
      mailListActions.attachTo('#list-actions');

      searchTrigger.attachTo('#search-trigger');
      resultsHighlighter.attachTo(document);

      mailSender.attachTo(document);

      mailService.attachTo(document);
      deleteService.attachTo(document);
      recoverService.attachTo(document);

      tags.attachTo(document);
      tagList.attachTo('#tag-list');

      router.attachTo(document);

      rightPaneDispatcher.attachTo(document);
      middlePaneDispatcher.attachTo(document);
      leftPaneDispatcher.attachTo(document);

      offCanvas.attachTo(document);
      userSettingsIcon.attachTo('#user-settings-icon');
      userSettingsBox.attachTo('#user-settings-box');
      logout.attachTo('#logout');
      logoutShortcut.attachTo('#logout-shortcut');
      version.attachTo('.version');

      feedback.attachTo('#feedback');
      feedbackSender.attachTo(document);
    }

    return initialize;
  }
);
