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
    'flight/lib/utils',
    'mail_list/ui/mail_item_factory',
    'page/router/url_params',
    'page/events'
  ],

  function (defineComponent, utils, MailItemFactory, urlParams, events) {
    'use strict';

    return defineComponent(mailList);

    function mailList () {
      var openMailEventFor = function (tag) {
        return tag === 'drafts' ? events.dispatchers.rightPane.openDraft : events.ui.mail.open;
      };

      this.defaultAttrs({
        mail: '.mail',
        currentMailIdent: '',
        urlParams: urlParams,
        initialized: false,
        checkedMails: {}
      });

      this.appendMail = function (mail) {
        var isChecked = mail.ident in this.attr.checkedMails;
        MailItemFactory.createAndAttach(this.$node, mail, this.attr.currentMailIdent, this.attr.currentTag, isChecked);
      };

      this.resetMailList = function () {
        this.trigger(document, events.mails.teardown);
        this.$node.empty();
      };

      this.triggerMailOpenForPopState = function (data) {
        if (data.mailIdent) {
          this.trigger(document, openMailEventFor(data.tag), { ident: data.mailIdent });
        }
      };

      this.shouldSelectEmailFromUrlMailIdent = function () {
        return this.attr.urlParams.hasMailIdent();
      };

      this.selectMailBasedOnUrlMailIdent = function () {
        var mailIdent = this.attr.urlParams.getMailIdent();
        this.trigger(document, openMailEventFor(this.attr.currentTag), { ident: mailIdent });
        this.trigger(document, events.router.pushState, { tag: this.attr.currentTag, mailIdent: mailIdent });
      };

      this.updateCurrentTagAndMail = function (data) {
        if (data.ident) {
          this.attr.currentMailIdent = data.ident;
        }

        this.attr.currentTag = data.tag || this.attr.currentTag;

        this.updateCheckAllCheckbox();
      };

      this.renderMails = function (mails) {
        _.each(mails, this.appendMail, this);
        this.trigger(document, events.search.highlightResults, {where: '#mail-list'});
        this.trigger(document, events.search.highlightResults, {where: '.mail-read-view__header'});
      };

      this.triggerScrollReset = function () {
        this.trigger(document, events.dispatchers.middlePane.resetScroll);
      };

      this.showMails = function (event, data) {
        this.updateCurrentTagAndMail(data);
        this.refreshMailList(null, data);
        this.triggerMailOpenForPopState(data);
        this.openMailFromUrl();
      };

      this.refreshMailList = function (ev, data) {
        if (ev) { // triggered by the event, so we need to refresh the tag list
          this.trigger(document, events.dispatchers.tags.refreshTagList, { skipMailListRefresh: true });
        }
        this.resetMailList();
        this.renderMails(data.mails);
      };

      this.updateSelected = function (ev, data) {
        if (data.ident !== this.attr.currentMailIdent) {
          this.attr.currentMailIdent = data.ident;
        }
      };

      this.cleanSelected = function () {
        this.attr.currentMailIdent = '';
        this.triggerScrollReset();
      };

      this.respondWithCheckedMails = function (ev, caller) {
        this.trigger(caller, events.ui.mail.hereChecked, {checkedMails: this.attr.checkedMails});
      };

      this.updateCheckAllCheckbox = function () {
        this.trigger(document, events.ui.mails.hasMailsChecked, _.keys(this.attr.checkedMails).length > 0);
      };

      this.addToCheckedMails = function (ev, data) {
        this.attr.checkedMails[data.mail.ident] = data.mail;
        this.updateCheckAllCheckbox();
      };

      this.removeFromCheckedMails = function (ev, data) {
        if (data.mails) {
          _.each(data.mails, function (mail) {
            delete this.attr.checkedMails[mail.ident];
          }, this);
        } else {
          delete this.attr.checkedMails[data.mail.ident];
        }
        this.updateCheckAllCheckbox();
      };

      this.refreshWithScroll = function () {
        this.trigger(document, events.ui.mails.refresh);
        this.triggerScrollReset();
      };

      this.refreshAfterSaveDraft = function () {
        if (this.attr.currentTag === 'drafts') {
          this.refreshWithScroll();
        }
      };

      this.refreshAfterMailSent = function () {
        if (this.attr.currentTag === 'drafts' || this.attr.currentTag === 'sent') {
          this.refreshWithScroll();
        }
      };

      this.after('initialize', function () {
        this.on(document, events.ui.mails.cleanSelected, this.cleanSelected);
        this.on(document, events.ui.tag.select, this.cleanSelected);

        this.on(document, events.mails.available, this.showMails);
        this.on(document, events.mails.availableForRefresh, this.refreshMailList);

        this.on(document, events.mail.draftSaved, this.refreshAfterSaveDraft);
        this.on(document, events.mail.sent, this.refreshAfterMailSent);

        this.on(document, events.ui.mail.updateSelected, this.updateSelected);
        this.on(document, events.ui.mail.wantChecked, this.respondWithCheckedMails);
        this.on(document, events.ui.mail.checked, this.addToCheckedMails);
        this.on(document, events.ui.mail.unchecked, this.removeFromCheckedMails);

        this.openMailFromUrl = utils.once(function () {
          if (this.shouldSelectEmailFromUrlMailIdent()) {
            this.selectMailBasedOnUrlMailIdent();
          }
        });

      });
    }
  }
);
