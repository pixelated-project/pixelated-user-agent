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
    'views/templates',
    'page/events'
  ],

  function (defineComponent, templates, events) {
    'use strict';

    return defineComponent(mailActions);

    function mailActions() {

      this.defaultAttrs({
        replyButtonTop: '#reply-button-top',
        viewMoreActions: '#view-more-actions',
        replyAllButtonTop: '#reply-all-button-top',
        getMailRaw: '#get-mail-raw',
        deleteButtonTop: '#delete-button-top',
        moreActions: '#more-actions'
      });


      this.displayMailActions = function () {

        this.$node.html(templates.mails.mailActions());

        this.select('moreActions').hide();

        this.on(this.select('replyButtonTop'), 'click', function () {
          this.trigger(document, events.ui.replyBox.showReply);
        }.bind(this));

        this.on(this.select('replyAllButtonTop'), 'click', function () {
          this.trigger(document, events.ui.replyBox.showReplyAll);
          this.select('moreActions').hide();
        }.bind(this));

        this.on(this.select('getMailRaw'), 'click', function () {
          this.trigger(document, events.ui.mail.downloadRaw, {mail: this.attr.mail});
          this.select('moreActions').hide();
        }.bind(this));

        this.on(this.select('deleteButtonTop'), 'click', function () {
          this.trigger(document, events.ui.mail.delete, {mail: this.attr.mail});
          this.select('moreActions').hide();
        }.bind(this));

        this.on(this.select('viewMoreActions'), 'click', function () {
          this.select('moreActions').toggle();
        }.bind(this));

        this.on(this.select('viewMoreActions'), 'blur', function (event) {
          var replyButtonTopHover = this.select('replyAllButtonTop').is(':hover');
          var downloadRaw = this.select('getMailRaw').is(':hover');
          var deleteButtonTopHover = this.select('deleteButtonTop').is(':hover');

          if (replyButtonTopHover || deleteButtonTopHover || downloadRaw) {
            event.preventDefault();
          } else {
            this.select('moreActions').hide();
          }
        }.bind(this));

      };

      this.after('initialize', function () {
        this.on(document, events.dispatchers.rightPane.clear, this.teardown);
        this.displayMailActions();
      });
    }
  }
);
