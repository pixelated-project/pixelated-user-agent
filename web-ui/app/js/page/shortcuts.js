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
      this.after('initialize', function () {
        this.on(document, 'keydown', $.proxy(onKeydown, this));
      });

      var composeBoxId = 'compose-box';
      var keyCodes = {
        ESC: 27,
        C: 67,
        ENTER: 13,
        FORWARD_SLASH: 191,
        S: 83
      };
      var modifierKeys = {
        META: "META",
        CTRL: "CTRL"
      };

      // make constants public
      this.keyCodes = keyCodes;
      this.composeBoxId = composeBoxId;

      function onKeydown(event) {
        tryGlobalKeyEvents(event, triggerOnDocument.call(this));

        if (composeBoxIsShown()) {
          tryMailCompositionKeyEvents(event, triggerOnDocument.call(this));
        } else {
          tryMailHandlingKeyEvents(event, triggerOnDocument.call(this));
        }
      }

      function triggerOnDocument() {
        var self = this;
        return function (event) {
          self.trigger(document, event);
        }
      }

      function tryGlobalKeyEvents(event, triggerFunc) {
        var globalKeyEvents = {};
        globalKeyEvents[keyCodes.ESC] = events.dispatchers.rightPane.openNoMessageSelected;

        if (!globalKeyEvents.hasOwnProperty(event.which)) return;

        triggerFunc(globalKeyEvents[event.which]);
        event.preventDefault();
      }

      function tryMailCompositionKeyEvents(event, triggerFunc) {
        var mailCompositionKeyEvents = {};
        mailCompositionKeyEvents[modifierKeys.CTRL + keyCodes.ENTER] = events.ui.mail.send;
        mailCompositionKeyEvents[modifierKeys.META + keyCodes.ENTER] = events.ui.mail.send;

        if (!mailCompositionKeyEvents.hasOwnProperty(modifierKey(event) + event.which)) return;

        event.preventDefault();
        return triggerFunc(mailCompositionKeyEvents[modifierKey(event) + event.which]);
      }

      function tryMailHandlingKeyEvents(event, triggerFunc) {
        if (isTriggeredOnInputField(event.target)) return;

        var mailHandlingKeyEvents = {};
        mailHandlingKeyEvents[keyCodes.S] = events.search.focus;
        mailHandlingKeyEvents[keyCodes.FORWARD_SLASH] = events.search.focus;
        mailHandlingKeyEvents[keyCodes.C] = events.dispatchers.rightPane.openComposeBox;

        if (!mailHandlingKeyEvents.hasOwnProperty(event.which)) return;

        event.preventDefault();
        return triggerFunc(mailHandlingKeyEvents[event.which]);
      }

      function modifierKey(event) {
        var modifierKey = "";
        if (event.ctrlKey === true) modifierKey = modifierKeys.CTRL;
        if (event.metaKey === true) modifierKey = modifierKeys.META;
        return modifierKey;
      }

      function isTriggeredOnInputField(element) {
        return $(element).is('input') || $(element).is('textarea');
      }

      function composeBoxIsShown() {
        return $('#' + composeBoxId).length;
      }
    }
  });
