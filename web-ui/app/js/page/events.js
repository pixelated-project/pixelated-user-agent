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
define(function () {
  'use strict';

  var events = {
    router: {
      pushState: 'router:pushState'
    },
    ui: {
      sendbutton: {
        enable: 'ui:sendbutton:enable'
      },
      middlePane: {
        expand: 'ui:middlePane:expand',
        contract: 'ui:middlePane:contract'
      },
      userAlerts: {
        displayMessage: 'ui:userAlerts:displayMessage'
      },
      tag: {
        selected: 'ui:tagSelected',
        select: 'ui:tagSelect'
      },
      tags: {
        loaded: 'ui:tagsLoaded'
      },
      tagList: {
        load: 'ui:tagList:load'
      },
      mails: {
        refresh: 'ui:mails:refresh',
        fetchByTag: 'ui:mails:fetchByTag',
        cleanSelected: 'ui:mails:cleanSelected',
        checkAll: 'ui:mails:checkAll',
        uncheckAll: 'ui:mails:uncheckAll',
        hasMailsChecked: 'ui:mails:hasMailsChecked'
      },
      mail: {
        open: 'ui:mail:open',
        updateSelected: 'ui:mail:updateSelected',
        delete: 'ui:mail:delete',
        deleteMany: 'ui:mail:deleteMany',
        recoverMany: 'ui:mail:recoverMany',
        wantChecked: 'ui:mail:wantChecked',
        hereChecked: 'ui:mail:hereChecked',
        checked: 'ui:mail:checked',
        unchecked: 'ui:mail:unchecked',
        changedSinceLastSave: 'ui:mail:changedSinceLastSave',
        send: 'ui:mail:send',
        recipientsUpdated: 'ui:mail:recipientsUpdated'
      },
      page: {
        previous: 'ui:page:previous',
        next: 'ui:page:next',
        changed: 'ui:page:changed'
      },
      composeBox: {
        newMessage: 'ui:composeBox:newMessage',
        newReply: 'ui:composeBox:newReply',
        trashReply: 'ui:composeBox:trashReply',
        requestCancelReply: 'ui:composeBox:requestCancelReply'
      },
      replyBox: {
        showReply: 'ui:replyBox:showReply',
        showReplyAll: 'ui:replyBox:showReplyAll'
      },
      recipients: {
        entered: 'ui:recipients:entered',
        updated: 'ui:recipients:updated',
        deleteRecipient: 'ui:recipients:deleteRecipient',
        deleteLast: 'ui:recipients:deleteLast',
        selectLast: 'ui:recipients:selectLast',
        unselectAll: 'ui:recipients:unselectAll',
        addressesExist: 'ui:recipients:addressesExist',
        inputFieldHasCharacters: 'ui:recipients:inputFieldHasCharacters',
        inputFieldIsEmpty: 'ui:recipients:inputFieldIsEmpty',
        doCompleteInput: 'ui:recipients:doCompleteInput',
        doCompleteRecipients: 'ui:recipients:doCompleteRecipients'
      }
    },
    search: {
      perform: 'search:perform',
      results: 'search:results',
      empty: 'search:empty',
      highlightResults: 'search:highlightResults',
      resetHighlight: 'search:resetHighlight'
    },
    mail: {
      here: 'mail:here',
      want: 'mail:want',
      send: 'mail:send',
      send_failed: 'mail:send_failed',
      sent: 'mail:sent',
      read: 'mail:read',
      unread: 'mail:unread',
      delete: 'mail:delete',
      deleteMany: 'mail:deleteMany',
      recoverMany: 'mail:recoverMany',
      deleted: 'mail:deleted',
      saveDraft: 'draft:save',
      draftSaved: 'draft:saved',
      draftReply: {
        want: 'mail:draftReply:want',
        here: 'mail:draftReply:here',
        notFound: 'mail:draftReply:notFound'
      },
      notFound: 'mail:notFound',
      save: 'mail:saved',
      tags: {
        update: 'mail:tags:update',
        updated: 'mail:tags:updated'
      }
    },
    mails: {
      available: 'mails:available',
      availableForRefresh: 'mails:available:refresh',
      teardown: 'mails:teardown'
    },
    tags: {
      want: 'tags:want',
      received: 'tags:received',
      teardown: 'tags:teardown',
      shortcuts: {
        teardown: 'tags:shortcuts:teardown'
      }
    },
    route: {
      toUrl: 'route:toUrl'
    },

    components: {
      composeBox: {
        open: 'components:composeBox:open',
        close: 'components:composeBox:close'
      },
      mailPane: {
        open: 'components:mailPane:open',
        close: 'components:mailPane:close'
      },
      mailView: {
        show: 'components:mailView:show',
        close: 'components:mailView:close'
      },
      replySection: {
        initialize: 'components:replySection:initialize',
        close: 'components:replySection:close'
      },
      noMessageSelectedPane: {
        open: 'components:noMessageSelectedPane:open',
        close: 'components:noMessageSelectedPane:close'
      }
    },

    dispatchers: {
      rightPane: {
        openComposeBox: 'dispatchers:rightPane:openComposeBox',
        openNoMessageSelected: 'dispatchers:rightPane:openNoMessageSelected',
        openNoMessageSelectedWithoutPushState: 'dispatchers:rightPane:openNoMessageSelectedWithoutPushState',
        refreshMailList: 'dispatchers:rightPane:refreshMailList',
        openDraft: 'dispatchers:rightPane:openDraft',
        selectTag: 'dispatchers:rightPane:selectTag',
        clear: 'dispatchers:rightPane:clear'
      },
      middlePane: {
        refreshMailList: 'dispatchers:middlePane:refreshMailList',
        cleanSelected: 'dispatchers:middlePane:unselect',
        resetScroll: 'dispatchers:middlePane:resetScroll'
      },
      tags: {
        refreshTagList: 'dispatchers:tag:refresh'
      }
    }
  };

  return events;
});
