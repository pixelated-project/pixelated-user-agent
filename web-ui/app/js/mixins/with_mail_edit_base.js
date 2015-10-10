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
    'helpers/view_helper',
    'mail_view/ui/recipients/recipients',
    'mail_view/ui/draft_save_status',
    'page/events',
    'views/i18n',
    'mail_view/ui/send_button',
    'mail_view/ui/draft_button',
    'flight/lib/utils'
  ],
  function(viewHelper, Recipients, DraftSaveStatus, events, i18n, SendButton, DraftButton, utils) {
    'use strict';

    function withMailEditBase() {

      this.defaultAttrs({
        bodyBox: '#text-box',
        sendButton: '#send-button',
        draftButton: '#draft-button',
        cancelButton: '#cancel-button',
        trashButton: '#trash-button',
        toArea: '#recipients-to-area',
        ccArea: '#recipients-cc-area',
        bccArea: '#recipients-bcc-area',
        ccsTrigger: '#ccs-trigger',
        bccsTrigger: '#bccs-trigger',
        toTrigger: '#to-trigger',
        subjectBox: '#subject',
        tipMsg: '.tip-msg',
        draftSaveStatus: '#draft-save-status',
        recipientsFields: '#recipients-fields',
        currentTag: '',
        recipientValues: {to: [], cc: [], bcc: []},
        saveDraftInterval: 3000
      });

      this.attachRecipients = function (context) {
        Recipients.attachTo(this.select('toArea'), { name: 'to', addresses: context.recipients.to });
        Recipients.attachTo(this.select('ccArea'), { name: 'cc', addresses: context.recipients.cc || []});
        Recipients.attachTo(this.select('bccArea'), { name: 'bcc', addresses: context.recipients.bcc || []});
      };

      function thereAreRecipientsToDisplay() {

        var allRecipients = _.chain(this.attr.recipientValues).
          values().
          flatten().
          remove(undefined).
          value();

        return !_.isEmpty(allRecipients);
      }

      this.warnSendButtonOfRecipients = function () {
        if (thereAreRecipientsToDisplay.call(this)) {
          _.forOwn(this.attr.recipientValues, function (recipients, recipientsType) {
            if (!_.isUndefined(recipients) && !_.isEmpty(recipients)) {
              var recipientsUpdatedData = {
                newRecipients: recipients,
                recipientsName: recipientsType
              };
              this.trigger(document, events.ui.recipients.updated, recipientsUpdatedData);
            }
          }.bind(this));
        }
      };

      this.render = function(template, context) {
        this.$node.html(template(context));

        if(!context || _.isEmpty(context)){
          context.recipients = {to: [], cc: [], bcc: []};
        }
        this.attr.recipientValues = context.recipients;
        this.attachRecipients(context);

        this.on(this.select('draftButton'), 'click', this.buildAndSaveDraft);
        this.on(this.select('trashButton'), 'click', this.trashMail);
        SendButton.attachTo(this.select('sendButton'));
        DraftButton.attachTo(this.select('draftButton'));

        this.warnSendButtonOfRecipients();
      };

      this.enableAutoSave = function () {
        this.select('bodyBox').on('input', this.monitorInput.bind(this));
        this.select('subjectBox').on('input', this.monitorInput.bind(this));
        DraftSaveStatus.attachTo(this.select('draftSaveStatus'));
      };

      this.deleteMail = function(data) {
        this.attr.ident = data.ident;
        var mail = this.buildMail();
        this.trigger(document, events.ui.mail.delete, { mail: mail });
      };

      this.monitorInput = function() {
        this.trigger(events.ui.mail.changedSinceLastSave);
        this.cancelPostponedSaveDraft();
        var mail = this.buildMail();
        this.postponeSaveDraft(mail);
      };

      this.trashMail = function() {
        this.cancelPostponedSaveDraft();
        this.trigger(document, events.mail.save, {
          mail: this.buildMail(),
          callback: this.deleteMail.bind(this)
        });
      };

      this.sendMail = function () {
        this.cancelPostponedSaveDraft();
        var mail = this.buildMail('sent');

        if (allRecipientsAreEmails(mail)) {
          this.trigger(events.mail.send, mail);
        } else {
          this.trigger(
            events.ui.userAlerts.displayMessage,
            {message: i18n('One or more of the recipients are not valid emails')}
          );
          this.trigger(events.mail.send_failed);
        }
      };

      this.buildAndSaveDraft = function () {
        var mail = this.buildMail();
        this.saveDraft(mail);
      };

      this.recipientsUpdated = function (ev, data) {
        this.attr.recipientValues[data.recipientsName] = data.newRecipients;
        this.trigger(document, events.ui.mail.recipientsUpdated);
        if (data.skipSaveDraft) { return; }

        this.attr.silent = true;
        var mail = this.buildMail();
        this.postponeSaveDraft(mail);
      };

      this.saveDraft = function (mail) {
        this.cancelPostponedSaveDraft();
        this.trigger(document, events.mail.saveDraft, mail);
      };

      this.cancelPostponedSaveDraft = function() {
        clearTimeout(this.attr.timeout);
      };

      this.postponeSaveDraft = function (mail) {
        this.cancelPostponedSaveDraft();

        this.attr.timeout = window.setTimeout(_.bind(function() {
          this.attr.silent = true;
          this.saveDraft(mail);
        }, this), this.attr.saveDraftInterval);
      };

      this.draftSaved = function(event, data) {
        this.attr.ident = data.ident;
        if(!this.attr.silent) {
          this.trigger(document, events.ui.userAlerts.displayMessage, { message: i18n('Saved as draft.') });
        }
        delete this.attr.silent;
      };

      this.validateAnyRecipient = function () {
        return !_.isEmpty(_.flatten(_.values(this.attr.recipientValues)));
      };

      function allRecipientsAreEmails(mail) {
        var allRecipients = mail.header.to.concat(mail.header.cc).concat(mail.header.bcc);
        return _.isEmpty(allRecipients) ? false : _.all(allRecipients, emailFormatChecker);
      }

      function emailFormatChecker(email) {
        var emailFormat = /[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailFormat.test(email);
      }

      this.saveTag = function(ev, data) {
        this.attr.currentTag = data.tag;
      };

      this.mailSent = function() {
        this.trigger(document, events.ui.userAlerts.displayMessage, { message: 'Your message was sent!' });
      };

      this.enableFloatlabel = function(element) {
        var showClass = 'showfloatlabel';
        $(element).bind('keyup', function() {
          var label = $(this).prev('label');
          if (this.value !== '') {
            label.addClass(showClass);
            $(this).addClass(showClass);
          } else {
            label.removeClass(showClass);
            $(this).removeClass(showClass);
          }
        });
      };

      this.after('initialize', function () {
        this.on(document, events.dispatchers.rightPane.clear, this.teardown);
        this.on(document, events.ui.recipients.updated, this.recipientsUpdated);
        this.on(document, events.mail.draftSaved, this.draftSaved);
        this.on(document, events.mail.sent, this.mailSent);

        this.on(document, events.ui.mail.send, this.sendMail);

        this.on(document, events.ui.tag.selected, this.saveTag);
        this.on(document, events.ui.tag.select, this.saveTag);
      });
    }

    return withMailEditBase;
  });
