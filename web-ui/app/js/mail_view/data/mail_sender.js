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
    'flight/lib/component',
    'mail_view/data/mail_builder',
    'page/events',
    'helpers/monitored_ajax',
    'features'
  ],
  function (defineComponent, mailBuilder, events, monitoredAjax, features) {
    'use strict';

    return defineComponent(mailSender);

    function mailSender() {
      function successSendingMail(on){
        return function(result) {
          on.trigger(document, events.mail.sent, result);
        };
      }

      function failureSendingMail(on) {
        return function(result) {
          on.trigger(document, events.mail.send_failed);
        };
      }

      function successSaveDraft(on){
        return function(result){
          on.trigger(document, events.mail.draftSaved, result);
        };
      }

      this.defaultAttrs({
        mailsResource: '/mails'
      });

      this.sendMail = function(event, data) {
        monitoredAjax.call(_, this, this.attr.mailsResource, {
          type: 'POST',
          dataType: 'json',
          contentType: 'application/json; charset=utf-8',
          data: JSON.stringify(data)
        }).done(successSendingMail(this)).fail(failureSendingMail(this));

      };

      this.saveMail = function(mail) {
        return monitoredAjax.call(_, this, this.attr.mailsResource, {
          type: 'PUT',
          dataType: 'json',
          contentType: 'application/json; charset=utf-8',
          data: JSON.stringify(mail),
          skipErrorMessage: true
        });
      };

      this.saveDraft = function(event, data) {
        this.saveMail(data)
          .done(successSaveDraft(this));
      };

      this.saveMailWithCallback = function(event, data) {
        this.saveMail(data.mail)
          .done(function(result) { return data.callback(result); })
          .fail(function(result) { return data.callback(result); });
      };

      this.after('initialize', function () {
        this.on(events.mail.send, this.sendMail);
        if(features.isEnabled('saveDraft')) {
          this.on(events.mail.saveDraft, this.saveDraft);
        }
        this.on(document, events.mail.save, this.saveMailWithCallback);
      });
    }
  });
