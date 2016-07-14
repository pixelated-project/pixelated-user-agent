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
      this.characterCodes = {
        ESC: 27,
        C: 67,
        ENTER: 13
      };

      var self = this;

      function sendMail() {
        this.trigger(document, events.ui.mail.send);
      }

      function closeComposeBox() {
        this.trigger(document, events.dispatchers.rightPane.openNoMessageSelected);
      }

      function openComposeBox() {
        this.trigger(document, events.dispatchers.rightPane.openComposeBox);
      }

      function isTriggeredOnInputField(event) {
        return $(event.target).is('input') || $(event.target).is('textarea');
      }

      function ctrlOrMetaEnterKey(event) {
        return (event.ctrlKey === true || event.metaKey === true) && event.which === self.characterCodes.ENTER;
      }

      function escapeKey(event) {
        return event.which === self.characterCodes.ESC;
      }

      function cKey(event) {
        return event.which === self.characterCodes.C;
      }

      function onKeydown(event) {
        if (escapeKey(event)) closeComposeBox.call(this);
        if (ctrlOrMetaEnterKey(event)) sendMail.call(this);

        if (isTriggeredOnInputField(event)) return;

        if (cKey(event)) openComposeBox.call(this);
        event.preventDefault();
      }

      this.after('initialize', function () {
        this.on(document, 'keydown', $.proxy(onKeydown, this));
      });
    }
  });
