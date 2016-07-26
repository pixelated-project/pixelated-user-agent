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

    return defineComponent(mailViewShortcuts);

    function mailViewShortcuts() {
      var keyCodes = {
        ENTER: 13
      };
      var modifierKeys = {
        META: "META",
        CTRL: "CTRL"
      };

      // make constants public
      this.keyCodes = keyCodes;

      this.after('initialize', function () {
        this.$node.on('keydown', _.bind(onKeydown, this));
      });

      function onKeydown(event) {
        tryMailCompositionKeyEvents(event, _.bind(this.trigger, this, document));
      }

      function tryMailCompositionKeyEvents(event, triggerFunc) {
        var mailCompositionKeyEvents = {};
        mailCompositionKeyEvents[modifierKeys.CTRL + keyCodes.ENTER] = events.ui.mail.send;
        mailCompositionKeyEvents[modifierKeys.META + keyCodes.ENTER] = events.ui.mail.send;

        if (!mailCompositionKeyEvents.hasOwnProperty(modifierKey(event) + event.which)) {
          return;
        }

        event.preventDefault();
        return triggerFunc(mailCompositionKeyEvents[modifierKey(event) + event.which]);
      }

      function modifierKey(event) {
        var modifierKey = "";
        if (event.ctrlKey === true) {
          modifierKey = modifierKeys.CTRL;
        }
        if (event.metaKey === true) {
          modifierKey = modifierKeys.META;
        }
        return modifierKey;
      }
    }
  });
