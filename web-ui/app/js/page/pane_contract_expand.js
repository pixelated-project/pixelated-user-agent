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

define(['flight/lib/component', 'page/events'], function (describeComponent, events) {

  return describeComponent(paneContractExpand);

  function paneContractExpand() {
    this.defaultAttrs({
      RIGHT_PANE_EXPAND_CLASSES: 'small-7 medium-7 large-7 columns',
      RIGHT_PANE_CONTRACT_CLASSES: 'small-7 medium-4 large-4 columns',
      MIDDLE_PANE_EXPAND_CLASSES: 'small-5 medium-8 large-8 columns no-padding',
      MIDDLE_PANE_CONTRACT_CLASSES: 'small-5 medium-5 large-5 columns no-padding'
    });

    this.expandMiddlePaneContractRightPane = function () {
      $('#middle-pane-container').attr('class', this.attr.MIDDLE_PANE_EXPAND_CLASSES);
      $('#right-pane').attr('class', this.attr.RIGHT_PANE_CONTRACT_CLASSES);
    };

    this.contractMiddlePaneExpandRightPane = function () {
      $('#middle-pane-container').attr('class', this.attr.MIDDLE_PANE_CONTRACT_CLASSES);
      $('#right-pane').attr('class', this.attr.RIGHT_PANE_EXPAND_CLASSES);
    };

    this.after('initialize', function () {
      this.on(document, events.ui.mail.open, this.contractMiddlePaneExpandRightPane);
      this.on(document, events.dispatchers.rightPane.openComposeBox, this.contractMiddlePaneExpandRightPane);
      this.on(document, events.dispatchers.rightPane.openDraft, this.contractMiddlePaneExpandRightPane);
      this.on(document, events.dispatchers.rightPane.openFeedbackBox, this.contractMiddlePaneExpandRightPane);
      this.on(document, events.dispatchers.rightPane.openNoMessageSelected, this.expandMiddlePaneContractRightPane);
      this.expandMiddlePaneContractRightPane();
    });

  }
});
