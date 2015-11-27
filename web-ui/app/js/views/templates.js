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

define(['hbs/templates'], function (templates) {
  'use strict';

  var Templates = {
    compose: {
      box: window.Pixelated['app/templates/compose/compose_box.hbs'],
      inlineBox: window.Pixelated['app/templates/compose/inline_box.hbs'],
      replySection: window.Pixelated['app/templates/compose/reply_section.hbs'],
      recipientInput: window.Pixelated['app/templates/compose/recipient_input.hbs'],
      fixedRecipient: window.Pixelated['app/templates/compose/fixed_recipient.hbs'],
      recipients: window.Pixelated['app/templates/compose/recipients.hbs'],
      feedback: window.Pixelated['app/templates/compose/feedback_box.hbs']
    },
    tags: {
      tagList: window.Pixelated['app/templates/tags/tag_list.hbs'],
      tag: window.Pixelated['app/templates/tags/tag.hbs'],
      tagInner: window.Pixelated['app/templates/tags/tag_inner.hbs'],
      shortcut: window.Pixelated['app/templates/tags/shortcut.hbs']
    },
    userAlerts: {
      message: window.Pixelated['app/templates/user_alerts/message.hbs']
    },
    mails: {
      single: window.Pixelated['app/templates/mails/single.hbs'],
      fullView: window.Pixelated['app/templates/mails/full_view.hbs'],
      mailActions: window.Pixelated['app/templates/mails/mail_actions.hbs'],
      draft: window.Pixelated['app/templates/mails/draft.hbs'],
      sent: window.Pixelated['app/templates/mails/sent.hbs'],
      trash: window.Pixelated['app/templates/mails/trash.hbs']
    },
    mailActions: {
      actionsBox: window.Pixelated['app/templates/mail_actions/actions_box.hbs'],
      trashActionsBox: window.Pixelated['app/templates/mail_actions/trash_actions_box.hbs'],
      composeTrigger: window.Pixelated['app/templates/mail_actions/compose_trigger.hbs'],
      refreshTrigger: window.Pixelated['app/templates/mail_actions/refresh_trigger.hbs'],
      paginationTrigger: window.Pixelated['app/templates/mail_actions/pagination_trigger.hbs']
    },
    noMessageSelected: window.Pixelated['app/templates/compose/no_message_selected.hbs'],
    noMailsAvailable: window.Pixelated['app/templates/compose/no_mails_available.hbs'],
    search: {
      trigger: window.Pixelated['app/templates/search/search_trigger.hbs']
    },
    page: {
      userSettingsIcon: window.Pixelated['app/templates/page/user_settings_icon.hbs'],
      userSettingsBox: window.Pixelated['app/templates/page/user_settings_box.hbs'],
      logout: window.Pixelated['app/templates/page/logout.hbs'],
      logoutShortcut: window.Pixelated['app/templates/page/logout_shortcut.hbs'],
      version: window.Pixelated['app/templates/page/version.hbs']
    },
    feedback: {
      feedback: window.Pixelated['app/templates/feedback/feedback_trigger.hbs']
    }
  };

  Handlebars.registerPartial('tag_inner', Templates.tags.tagInner);
  Handlebars.registerPartial('recipients', Templates.compose.recipients);

  return Templates;
});
