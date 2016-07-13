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
      this.CHARACTER_CODES = {
        ESC: 27,
        C: 67
      };
      this.onKeydown = function (event) {
        if (event.which === this.CHARACTER_CODES.ESC) this.trigger(document, events.dispatchers.rightPane.openNoMessageSelected);
        if ($(event.target).is('input') || $(event.target).is('textarea')) return;
        if (event.which === this.CHARACTER_CODES.C) this.trigger(document, events.dispatchers.rightPane.openComposeBox);
        event.preventDefault();
      };

      this.after('initialize', function () {
        this.on(document, 'keydown', this.onKeydown);
      });
    }
  });
