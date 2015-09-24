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
    'mail_view/ui/compose_box',
    'mail_view/ui/mail_view',
    'mail_view/ui/reply_section',
    'mail_view/ui/draft_box',
    'mail_view/ui/no_message_selected_pane',
    'mail_view/ui/feedback_box',
    'page/events'
  ],

  function(defineComponent, ComposeBox, MailView, ReplySection, DraftBox, NoMessageSelectedPane, FeedbackBox, events) {
    'use strict';

    return defineComponent(rightPaneDispatcher);

    function rightPaneDispatcher() {
      this.defaultAttrs({
        rightPane: '#right-pane',
        composeBox: 'compose-box',
        feedbackBox: 'feedback-box',
        mailView: 'mail-view',
        noMessageSelectedPane: 'no-message-selected-pane',
        replySection: 'reply-section',
        draftBox: 'draft-box',
        currentTag: ''
      });

      this.createAndAttach = function(newContainer) {
        var stage = $('<div>', { id: newContainer });
        this.select('rightPane').append(stage);
        return stage;
      };

      this.reset = function (newContainer) {
        this.trigger(document, events.dispatchers.rightPane.clear);
        this.select('rightPane').empty();
        var stage = this.createAndAttach(newContainer);
        return stage;
      };

      this.openComposeBox = function() {
        var stage = this.reset(this.attr.composeBox);
        ComposeBox.attachTo(stage, {currentTag: this.attr.currentTag});
      };

      this.openFeedbackBox = function() {
        var stage = this.reset(this.attr.feedbackBox);
        FeedbackBox.attachTo(stage);
      };

      this.openMail = function(ev, data) {
        var stage = this.reset(this.attr.mailView);
        MailView.attachTo(stage, data);

        var replySectionContainer = this.createAndAttach(this.attr.replySection);
        ReplySection.attachTo(replySectionContainer, { ident: data.ident });
      };

      this.initializeNoMessageSelectedPane = function () {
        var stage = this.reset(this.attr.noMessageSelectedPane);
        NoMessageSelectedPane.attachTo(stage);
        this.trigger(document, events.dispatchers.middlePane.cleanSelected);
      };

      this.openNoMessageSelectedPane = function(ev, data) {
        this.initializeNoMessageSelectedPane();

        this.trigger(document, events.router.pushState, { tag: this.attr.currentTag, isDisplayNoMessageSelected: true });
      };

      this.openDraft = function (ev, data) {
        var stage = this.reset(this.attr.draftBox);
        DraftBox.attachTo(stage, { mailIdent: data.ident, currentTag: this.attr.currentTag });
      };

      this.selectTag = function(ev, data) {
        this.trigger(document, events.ui.tags.loaded, {tag: data.tag});
      };

      this.saveTag = function(ev, data) {
        this.attr.currentTag = data.tag;
      };

      this.after('initialize', function () {
        this.on(document, events.dispatchers.rightPane.openComposeBox, this.openComposeBox);
        this.on(document, events.dispatchers.rightPane.openDraft, this.openDraft);
        this.on(document, events.ui.mail.open, this.openMail);
        this.on(document, events.dispatchers.rightPane.openFeedbackBox, this.openFeedbackBox);
        this.on(document, events.dispatchers.rightPane.openNoMessageSelected, this.openNoMessageSelectedPane);
        this.on(document, events.dispatchers.rightPane.selectTag, this.selectTag);
        this.on(document, events.ui.tag.selected, this.saveTag);
        this.on(document, events.ui.tag.select, this.saveTag);
        this.on(document, events.dispatchers.rightPane.openNoMessageSelectedWithoutPushState, this.initializeNoMessageSelectedPane);
        this.initializeNoMessageSelectedPane();
      });
    }
  }
);
