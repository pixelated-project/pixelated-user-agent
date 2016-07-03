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
    'views/i18n',
    'services/model/mail',
    'helpers/monitored_ajax',
    'page/events',
    'features',
    'mixins/with_auto_refresh',
    'page/router/url_params',
  ], function (defineComponent, i18n, Mail, monitoredAjax, events, features, withAutoRefresh, urlParams) {

    'use strict';

    return defineComponent(mailService, withAutoRefresh('refreshMails'));

    function mailService() {
      var that;

      this.defaultAttrs({
        mailsResource: '/mails',
        singleMailResource: '/mail',
        currentTag: '',
        lastQuery: '',
        currentPage: 1,
        numPages: 1,
        pageSize: 25
      });

      this.errorMessage = function (msg) {
        return function () {
          that.trigger(document, events.ui.userAlerts.displayMessage, { message: msg });
        };
      };

      this.updateTags = function (ev, data) {
        var ident = data.ident;

        var success = function (data) {
          this.refreshMails();
          $(document).trigger(events.mail.tags.updated, { ident: ident, tags: data.tags });
          $(document).trigger(events.dispatchers.tags.refreshTagList, { skipMailListRefresh: true });
        };

        var failure = function (resp) {
          var msg = i18n.t('failed-change-tags');
          if (resp.status === 403) {
            msg = i18n.t('invalid-tag-name');
          }
          this.trigger(document, events.ui.userAlerts.displayMessage, { message: msg });
        };

        monitoredAjax(this, '/mail/' + ident + '/tags', {
          type: 'POST',
          contentType: 'application/json; charset=utf-8',
          data: JSON.stringify({newtags: data.tags})
        }).done(success.bind(this)).fail(failure.bind(this));

      };

      this.readMail = function (ev, data) {
        var mailIdents;
        if (data.checkedMails) {
          mailIdents = _.map(data.checkedMails, function (mail) {
            return mail.ident;
          });
        } else {
          mailIdents = [data.ident];
        }
        monitoredAjax(this, '/mails/read', {
          type: 'POST',
          data: JSON.stringify({idents: mailIdents})
        }).done(this.triggerMailsRead(data.checkedMails));
      };

      this.unreadMail = function (ev, data) {
        var mailIdents;
        if (data.checkedMails) {
          mailIdents = _.map(data.checkedMails, function (mail) {
            return mail.ident;
          });
        } else {
          mailIdents = [data.ident];
        }
        monitoredAjax(this, '/mails/unread', {
          type: 'POST',
          data: JSON.stringify({idents: mailIdents})
        }).done(this.triggerMailsRead(data.checkedMails));
      };

      this.triggerMailsRead = function (mails) {
        return _.bind(function () {
          this.refreshMails();
          this.trigger(document, events.ui.mails.uncheckAll);
        }, this);
      };

      this.triggerDeleted = function (dataToDelete) {
        return _.bind(function () {
          var mails = dataToDelete.mails || [dataToDelete.mail];

          this.refreshMails();
          this.trigger(document, events.ui.userAlerts.displayMessage, { message: dataToDelete.successMessage});
          this.trigger(document, events.ui.mails.uncheckAll);
          this.trigger(document, events.mail.deleted, { mails: mails });
        }, this);
      };

      this.triggerRecovered = function (dataToRecover) {
        return _.bind(function () {
          var mails = dataToRecover.mails || [dataToRecover.mail];

          this.refreshMails();
          this.trigger(document, events.ui.userAlerts.displayMessage, { message: i18n.t(dataToRecover.successMessage)});
          this.trigger(document, events.ui.mails.uncheckAll);
        }, this);
      };

      this.triggerArchived = function (dataToArchive) {
        return _.bind(function (response) {
          this.refreshMails();
          this.trigger(document, events.ui.userAlerts.displayMessage, { message: i18n.t(response.successMessage)});
          this.trigger(document, events.ui.mails.uncheckAll);
        }, this);
      };

      this.archiveManyMails = function(event, dataToArchive) {
        var mailIdents = _.map(dataToArchive.checkedMails, function (mail) {
          return mail.ident;
        });
        monitoredAjax(this, '/mails/archive', {
          type: 'POST',
          dataType: 'json',
          contentType: 'application/json; charset=utf-8',
          data: JSON.stringify({idents: mailIdents})
        }).done(this.triggerArchived(dataToArchive))
          .fail(this.errorMessage(i18n.t('failed-archive')));
      };

      this.deleteMail = function (ev, data) {
        monitoredAjax(this, '/mail/' + data.mail.ident,
          {type: 'DELETE'})
          .done(this.triggerDeleted(data))
          .fail(this.errorMessage(i18n.t('failed-delete-single')));
      };

      this.deleteManyMails = function (ev, data) {
        var dataToDelete = data;
        var mailIdents = _.map(data.mails, function (mail) {
          return mail.ident;
        });

        monitoredAjax(this, '/mails/delete', {
          type: 'POST',
          dataType: 'json',
          contentType: 'application/json; charset=utf-8',
          data: JSON.stringify({idents: mailIdents})
        }).done(this.triggerDeleted(dataToDelete))
          .fail(this.errorMessage(i18n.t('failed-delete-bulk')));
      };

      this.recoverManyMails = function (ev, data) {
        var dataToRecover = data;
        var mailIdents = _.map(data.mails, function (mail) {
          return mail.ident;
        });

        monitoredAjax(this, '/mails/recover', {
          type: 'POST',
          dataType: 'json',
          contentType: 'application/json; charset=utf-8',
          data: JSON.stringify({idents: mailIdents})
        }).done(this.triggerRecovered(dataToRecover))
          .fail(this.errorMessage(i18n.t('Could not move emails to inbox')));
      };

      function compileQuery(data) {
        var query = 'tag:"' + that.attr.currentTag + '"';

        if (data.tag === 'all') {
          query = 'in:all';
        }
        return query;
      }

      this.fetchByTag = function (ev, data) {
        this.attr.currentTag = data.tag;
        this.attr.lastQuery = compileQuery(data);
        this.updateCurrentPageNumber(1);

        this.refreshMails();
      };

      this.newSearch = function (ev, data) {
        this.attr.lastQuery = data.query;
        this.attr.currentTag = 'all';
        this.refreshMails();
      };

      this.mailFromJSON = function (mail) {
        return Mail.create(mail);
      };

      this.parseMails = function (data) {
        data.mails = _.map(data.mails, this.mailFromJSON, this);

        return data;
      };

      function escaped(s) {
        return encodeURIComponent(s);
      }

      this.excludeTrashedEmailsForDraftsAndSent = function (query) {
        if (query === 'tag:"drafts"' || query === 'tag:"sent"') {
          return query + ' -in:"trash"';
        }
        return query;
      };

      this.refreshMails = function () {
        var url = this.attr.mailsResource + '?q=' + escaped(this.attr.lastQuery) + '&p=' + this.attr.currentPage + '&w=' + this.attr.pageSize;

        this.attr.lastQuery = this.excludeTrashedEmailsForDraftsAndSent(this.attr.lastQuery);

        monitoredAjax(this, url, { dataType: 'json' })
          .done(function (data) {
            this.attr.numPages = Math.ceil(data.stats.total / this.attr.pageSize);
            this.trigger(document, events.mails.available, _.merge({tag: this.attr.currentTag, forSearch: this.attr.lastQuery }, this.parseMails(data)));
          }.bind(this))
          .fail(function () {
            this.trigger(document, events.ui.userAlerts.displayMessage, { message: i18n.t('failed-fetch-messages'), class: 'error' });
          }.bind(this));
      };

      function createSingleMailUrl(mailsResource, ident) {
        return mailsResource + '/' + ident;
      }

      this.fetchSingle = function (event, data) {
        var fetchUrl = createSingleMailUrl(this.attr.singleMailResource, data.mail);

        monitoredAjax(this, fetchUrl, { dataType: 'json' })
          .done(function (mail) {
            if (_.isNull(mail)) {
              this.trigger(data.caller, events.mail.notFound);
              return;
            }

            this.trigger(data.caller, events.mail.here, { mail: this.mailFromJSON(mail) });
          }.bind(this));
      };

      this.previousPage = function () {
        if (this.attr.currentPage > 1) {
          this.updateCurrentPageNumber(this.attr.currentPage - 1);
          this.refreshMails();
        }
      };

      this.downloadRaw = function (event, data) {
          monitoredAjax(this, '/mail/' + data.mail.ident,
          {type: 'POST'})
          .done(function (data) {
          var a=document.createElement('a');
            a.href='data:text/plain;base64,'+btoa(data.textPlainBody);
            a.textContent='download';
            a.download='raw_mail_content.txt';
            a.click();
            return;
           })
          .fail(this.errorMessage('Failed to download'));
      }

      this.nextPage = function () {
        if (this.attr.currentPage < (this.attr.numPages)) {
          this.updateCurrentPageNumber(this.attr.currentPage + 1);
          this.refreshMails();
        }
      };

      this.updateCurrentPageNumber = function (newCurrentPage) {
        this.attr.currentPage = newCurrentPage;
        this.trigger(document, events.ui.page.changed, {
          currentPage: this.attr.currentPage,
          numPages: this.attr.numPages
        });
      };

      this.wantDraftReplyForMail = function (ev, data) {
        if (!features.isEnabled('draftReply')) {
          this.trigger(document, events.mail.draftReply.notFound);
          return;
        }

        monitoredAjax(this, '/draft_reply_for/' + data.ident, { dataType: 'json' })
          .done(function (mail) {
            if (_.isNull(mail)) {
              this.trigger(document, events.mail.draftReply.notFound);
              return;
            }
            this.trigger(document, events.mail.draftReply.here, { mail: this.mailFromJSON(mail) });
          }.bind(this));
      };

      this.after('initialize', function () {
        that = this;

        if (features.isEnabled('tags')) {
          this.on(events.mail.tags.update, this.updateTags);
        }

        this.on(document, events.mail.draftReply.want, this.wantDraftReplyForMail);
        this.on(document, events.mail.want, this.fetchSingle);
        this.on(document, events.mail.read, this.readMail);
        this.on(document, events.mail.unread, this.unreadMail);
        this.on(document, events.mail.delete, this.deleteMail);
        this.on(document, events.mail.deleteMany, this.deleteManyMails);
        this.on(document, events.mail.recoverMany, this.recoverManyMails);
        this.on(document, events.mail.archiveMany, this.archiveManyMails);
        this.on(document, events.search.perform, this.newSearch);
        this.on(document, events.ui.tag.selected, this.fetchByTag);
        this.on(document, events.ui.tag.select, this.fetchByTag);
        this.on(document, events.ui.mails.refresh, this.refreshMails);
        this.on(document, events.ui.page.previous, this.previousPage);
        this.on(document, events.ui.page.next, this.nextPage);
        this.on(document, events.ui.mail.downloadRaw, this.downloadRaw);

        this.fetchByTag(null, {tag: urlParams.getTag()});
      });
    }
  }
);
