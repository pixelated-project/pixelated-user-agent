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
'use strict';
define(['flight/lib/component', 'page/events'], function (defineComponent, events) {

  return defineComponent(function() {

    this.closeSlider = function (ev){
      $('.off-canvas-wrap.content').removeClass('move-right');
      this.toggleTagsVisibility();
    };

    this.toggleSlideContent = function (ev) {
      ev.preventDefault();
  	  $('.left-off-canvas-toggle').click();
	    this.toggleTagsVisibility();
    };

    this.toggleTagsVisibility = function () {
      if ($('.off-canvas-wrap.content').hasClass('move-right')) {
        $('#left-pane').addClass('expanded');
        $('#custom-tag-list').addClass('expanded');
      } else {
        $('#left-pane').removeClass('expanded');
        $('#custom-tag-list').removeClass('expanded');
      }
    };

    this.after('initialize', function () {
      this.on($('#middle-pane-container'), 'click', this.closeSlider);
      this.on($('#right-pane'), 'click', this.closeSlider);
      this.on($('.side-nav-toggle'), 'click', this.toggleSlideContent);
    });
  });
});
