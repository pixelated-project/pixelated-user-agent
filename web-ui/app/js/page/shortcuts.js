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

define([
    'flight/lib/component',
    'page/events'
  ],
  function (defineComponent, events) {
    'use strict';

    return defineComponent(shortcuts);

    function shortcuts() {
      var composeBoxId = 'compose-box';
      var keyCodes = {
        C: 67,
        FORWARD_SLASH: 191,
        S: 83
      };

      // make constants public
      this.keyCodes = keyCodes;
      this.composeBoxId = composeBoxId;

      this.after('initialize', function () {
        this.on('keydown', _.partial(tryMailHandlingKeyEvents, _.bind(this.trigger, this, document)));
      });

      function tryMailHandlingKeyEvents(triggerFunc, event) {
        if (isTriggeredOnInputField(event.target) || composeBoxIsShown()) {
          return;
        }

        var mailHandlingKeyEvents = {};
        mailHandlingKeyEvents[keyCodes.S] = events.search.focus;
        mailHandlingKeyEvents[keyCodes.FORWARD_SLASH] = events.search.focus;
        mailHandlingKeyEvents[keyCodes.C] = events.dispatchers.rightPane.openComposeBox;

        if (!mailHandlingKeyEvents.hasOwnProperty(event.which)) {
          return;
        }

        event.preventDefault();
        return triggerFunc(mailHandlingKeyEvents[event.which]);
      }

      function isTriggeredOnInputField(element) {
        return $(element).is('input') || $(element).is('textarea');
      }

      function composeBoxIsShown() {
        return $('#' + composeBoxId).length;
      }
    }
  });
