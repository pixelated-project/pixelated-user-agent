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
define(['flight/lib/component', 'features', 'views/templates', 'page/events'], function (defineComponent, features, templates, events) {
  'use strict';

  return defineComponent(function () {
    this.defaultAttrs({
      close: '#user-settings-close'
    });

    this.render = function () {
      this.$node.html(templates.page.userSettingsBox());
      if (features.isLogoutEnabled()) {
        this.$node.addClass('extra-bottom-space');
      }
    };

    this.toggleHidden = function() {
      if (this.$node.hasClass('hidden')) {
        this.$node.removeClass('hidden');
      } else {
        this.$node.addClass('hidden');
      }
    };

    this.after('initialize', function () {
      this.render();
      this.on(document, events.ui.userSettingsBox.toggle, this.toggleHidden);
      this.on(this.attr.close, 'click', this.toggleHidden);
    });
  });
});
