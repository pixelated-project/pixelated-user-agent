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
define(
  [
    'flight/lib/component',
    'helpers/monitored_ajax',
    'page/events'
  ],
  function (defineComponent, monitoredAjax, events) {
    'use strict';

  return defineComponent(function () {
    this.defaultAttrs({
      feedbackResource: '/feedback'
    });

    this.successSubmittingFeedback = function() {
      this.trigger(document, events.feedback.submitted);
    };

    this.submitFeedback = function(event, data) {
      monitoredAjax.call(_, this, this.attr.feedbackResource, {
        type: 'POST',
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        data: JSON.stringify(data)
      }).done(this.successSubmittingFeedback());
    };

    this.after('initialize', function () {
      this.on(document, events.feedback.submit, this.submitFeedback);
    });

  });
});
