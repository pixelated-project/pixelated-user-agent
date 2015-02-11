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

define(['flight/lib/component', 'page/events', 'views/i18n'], function (defineComponent, events, i18n) {
  'use strict';

  return defineComponent(function() {

    this.successDeleteMessageFor = function(mail) {
      return mail.isInTrash() ?
        i18n('Your message was permanently deleted!') :
        i18n('Your message was moved to trash!');
    };

    this.successDeleteManyMessageFor = function(mail) {
      return mail.isInTrash() ?
        i18n('Your messages were permanently deleted!') :
        i18n('Your messages were moved to trash!');
    };

    this.deleteEmail = function (event, data) {
      this.trigger(document, events.mail.delete, {
        mail: data.mail,
        successMessage: this.successDeleteMessageFor(data.mail)
      });
    };

    this.deleteManyEmails = function (event, data) {
      var emails = _.values(data.checkedMails);
      var firstEmail = emails[_.first(_.keys(emails))];

      this.trigger(document, events.mail.deleteMany, {
        mails: emails,
        successMessage: this.successDeleteManyMessageFor(firstEmail)
      });

    };

    this.after('initialize', function () {
      this.on(document, events.ui.mail.delete, this.deleteEmail);
      this.on(document, events.ui.mail.deleteMany, this.deleteManyEmails);
    });

  });
});
