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

      this.keyCodes = {
        ESC: 27,
        C: 67,
        ENTER: 13,
        FORWARD_SLASH: 191,
        S: 83
      };

      var specialKeyToEvent = {};
      specialKeyToEvent[this.keyCodes.ESC] = events.dispatchers.rightPane.openNoMessageSelected;

      var alphaNumericKeyToEvent = {};
      alphaNumericKeyToEvent[this.keyCodes.S] = events.search.focus;
      alphaNumericKeyToEvent[this.keyCodes.FORWARD_SLASH] = events.search.focus;
      alphaNumericKeyToEvent[this.keyCodes.C] = events.dispatchers.rightPane.openComposeBox;

      function onKeydown(event) {
        if (ctrlOrMetaEnterKey.call(this, event)) sendMail.call(this);
        if (specialKeyToEvent.hasOwnProperty(event.which))
          this.trigger(document, specialKeyToEvent[event.which]);

        if (isTriggeredOnInputField(event)) return;

        if (alphaNumericKeyToEvent.hasOwnProperty(event.which))
          this.trigger(document, alphaNumericKeyToEvent[event.which]);
        event.preventDefault();
      }

      function sendMail() {
        this.trigger(document, events.ui.mail.send);
      }

      function isTriggeredOnInputField(event) {
        return $(event.target).is('input') || $(event.target).is('textarea');
      }

      function ctrlOrMetaEnterKey(event) {
        return (event.ctrlKey === true || event.metaKey === true) && event.which === this.keyCodes.ENTER;
      }
    }
  });
