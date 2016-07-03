/*
 * Copyright (c) 2015 ThoughtWorks, Inc.
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

define(['flight/lib/component', 'views/templates', 'page/events', 'features', 'feedback/feedback_cache'],
  function (defineComponent, templates, events, features, feedbackCache) {
    'use strict';

    return defineComponent(function () {
      this.defaultAttrs({
        'closeButton': '.close-mail-button',
        'submitButton': '#send-button',
        'textBox': '#text-box',
      });

      this.render = function () {
        this.$node.html(templates.compose.feedback());
      };

      this.startCachingData = function () {
        this.select('textBox').val(feedbackCache.getCache());
        this.select('textBox').on('change', this.cacheFeedbackData.bind(this));
      };


      this.cacheFeedbackData = function () {
        feedbackCache.setCache(this.select('textBox').val());
      };

      this.showNoMessageSelected = function () {
        this.trigger(document, events.dispatchers.rightPane.openNoMessageSelected);
      };

      this.submitFeedback = function () {
        var feedback = this.select('textBox').val();
        this.trigger(document, events.feedback.submit, {feedback: feedback});
        feedbackCache.resetCache();
      };

      this.showSuccessMessage = function () {
        this.trigger(document, events.ui.userAlerts.displayMessage, {message: 'Thanks for your feedback!'});
      };

      this.after('initialize', function () {
        if (features.isEnabled('feedback')) {
          this.render();
          this.startCachingData();
          this.on(document, events.feedback.submitted, this.showNoMessageSelected);
          this.on(document, events.feedback.submitted, this.showSuccessMessage);
          this.on(this.select('closeButton'), 'click', this.showNoMessageSelected);
          this.on(this.select('submitButton'), 'click', this.submitFeedback);
        }
      });

    });
  });
