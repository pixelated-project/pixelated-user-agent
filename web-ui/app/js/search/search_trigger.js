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

define(
  [
    'flight/lib/component',
    'views/templates',
    'page/events',
    'views/i18n'
  ], function (defineComponent, templates, events, i18n) {

    'use strict';

    return defineComponent(searchTrigger);

    function searchTrigger() {
      this.defaultAttrs({
        input: 'input[type=search]',
        form: 'form',
        searchResultsPrefix: 'search-results-for'
      });

      this.render = function() {
        this.$node.html(templates.search.trigger());
      };

      this.search = function(ev, data) {
        this.trigger(document, events.search.resetHighlight);
        ev.preventDefault();
        var input = this.select('input');
        var value = input.val();
        input.blur();
        if(!_.isEmpty(value)){
          this.trigger(document, events.search.perform, { query: value });
        } else {
          this.trigger(document, events.search.empty);
        }
      };

      this.clearInput = function() {
        this.select('input').val('');
      };

      this.showOnlySearchTerms = function(event){
        var value = this.select('input').val();
        var searchTerms = value.slice((i18n.t(this.attr.searchResultsPrefix) + ': ').length);
        this.select('input').val(searchTerms);
      };

      this.showSearchTermsAndPlaceHolder = function(event){
        var value = this.select('input').val();
        if (value.length > 0){
          this.select('input').val(i18n.t(this.attr.searchResultsPrefix) + ': ' + value);
        }
      };

      this.focus = function () {
        this.select('input').focus();
      };

      this.after('initialize', function () {
        this.render();
        this.on(this.select('form'), 'submit', this.search);
        this.on(this.select('input'), 'focus', this.showOnlySearchTerms);
        this.on(this.select('input'), 'blur', this.showSearchTermsAndPlaceHolder);
        this.on(document, events.ui.tag.selected, this.clearInput);
        this.on(document, events.ui.tag.select, this.clearInput);
        this.on(document, events.search.focus, this.focus);
      });
    }
  }
);
