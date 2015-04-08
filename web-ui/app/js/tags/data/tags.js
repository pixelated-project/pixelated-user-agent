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
define(['flight/lib/component', 'page/events', 'helpers/monitored_ajax', 'mixins/with_feature_toggle', 'mixins/with_auto_refresh'], function (defineComponent, events, monitoredAjax,  withFeatureToggle, withAutoRefresh) {
  'use strict';

  var DataTags = defineComponent(dataTags, withFeatureToggle('tags', function() {
    $(document).trigger(events.ui.mails.refresh);
  }), withAutoRefresh('refreshTags'));

  DataTags.all = {
    name: 'all',
    ident: '8752888923742657436',
    query: 'in:all',
    default: true,
    counts:{
      total:0,
        read:0,
        starred:0,
        replied:0
    }
  };

  function dataTags() {
    function sendTagsBackTo(on, params) {
      return function(data) {
        data.push(DataTags.all);
        on.trigger(params.caller, events.tags.received, {tags: data});
      };
    }

    this.defaultAttrs({
      tagsResource: '/tags'
    });

    this.fetchTags = function(event, params) {
      monitoredAjax(this, this.attr.tagsResource)
        .done(sendTagsBackTo(this, params));
    };

    this.refreshTags = function() {
      this.fetchTags(null, {caller: document});
    };

    this.after('initialize', function () {
      this.on(document, events.tags.want, this.fetchTags);
      this.on(document, events.mail.sent, this.fetchTags);
    });
  }

  return DataTags;
});
