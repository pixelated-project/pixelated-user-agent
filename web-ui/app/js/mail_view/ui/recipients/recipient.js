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
    'page/events'
  ],

  function (defineComponent, templates, events) {
  'use strict';

    return defineComponent(recipient);

    function recipient() {
      this.renderAndPrepend = function (nodeToPrependTo, recipient) {
        var html = $(templates.compose.fixedRecipient(recipient));
        html.insertBefore(nodeToPrependTo.children().last());
        var component = new this.constructor();
        component.initialize(html, recipient);
        component.attr.recipient = recipient;
        return component;
      };

      this.recipientDelActions = function () {
        this.on(this.$node.find('.recipient-del'), 'click', function (event) {
          this.doSelect();
          this.trigger(events.ui.recipients.deleteRecipient, this);
          event.preventDefault();
        });

        this.on(this.$node.find('.recipient-del'), 'mouseover', function () {
          this.$node.find('.recipient-value').addClass('deleting');
          this.$node.find('.recipient-del').addClass('deleteTooltip');
        });

        this.on(this.$node.find('.recipient-del'), 'mouseout', function () {
          this.$node.find('.recipient-value').removeClass('deleting');
          this.$node.find('.recipient-del').removeClass('deleteTooltip');
        });
      };

      this.destroy = function () {
        this.$node.remove();
        this.teardown();
      };

      this.doSelect = function () {
        this.$node.find('.recipient-value').addClass('selected');
      };

      this.doUnselect = function () {
        this.$node.find('.recipient-value').removeClass('selected');
      };

      this.isSelected = function () {
        return this.$node.find('.recipient-value').hasClass('selected');
      };

      this.sinalizeInvalid = function () {
        this.$node.find('.recipient-value>span').addClass('invalid-format');
      };

      this.discoverEncryption = function () {
        this.$node.addClass('discover-encryption');
        var p = $.getJSON('/keys?search=' + this.attr.address).promise();
        p.done(function () {
          this.$node.find('.recipient-value').addClass('encrypted');
          this.$node.removeClass('discover-encryption');
        }.bind(this));
          p.fail(function () {
            this.$node.find('.recipient-value').addClass('not-encrypted').addClass('fa').addClass('fa-unlock');
            this.$node.removeClass('discover-encryption');
        }.bind(this));
      };

      this.getMailAddress = function() {
        return this.$node.find('input[type=hidden]').val();
      };

      this.triggerEditRecipient = function(event, element) {
        this.trigger(this.$node.closest('.recipients-area'), events.ui.recipients.clickToEdit, this);
      };

      this.after('initialize', function () {
        this.recipientDelActions();
        this.on('click', this.triggerEditRecipient);
        
        if (this.attr.invalidAddress){
            this.sinalizeInvalid();
        } else {
            this.discoverEncryption();
        }
      });
    }
  }
);
