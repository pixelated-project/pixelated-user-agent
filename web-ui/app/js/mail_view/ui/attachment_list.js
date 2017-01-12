/*
 * Copyright (c) 2015 ThoughtWorks, Inc.
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
        'views/templates',
        'page/events',
        'helpers/view_helper',
        'helpers/monitored_ajax'
    ],

    function (templates, events, viewHelper, monitoredAjax) {
        'use strict';

        function attachmentList() {
            this.defaultAttrs({
                inputFileUpload: '#fileupload',
                attachmentListItem: '#attachment-list-item',
                attachmentUploadItem: '#attachment-upload-item',
                attachmentUploadItemProgress: '#attachment-upload-item-progress',
                attachmentUploadItemAbort: '#attachment-upload-item-abort',
                attachmentBaseUrl: '/attachment',
                attachments: [],
                closeIcon: '#upload-error-close',
                uploadError: '#upload-error',
                dismissButton: '#dismiss-button',
                uploadFileButton: '#upload-file-button'
            });

            var ONE_MEGABYTE = 1024*1024;
            var ATTACHMENT_SIZE_LIMIT = 5*ONE_MEGABYTE;

            this.showAttachment = function (ev, data) {
                this.trigger(document, events.mail.appendAttachment, data);
                this.renderAttachmentListView(data);
            };

            this.addAttachment = function (event, data) {
                this.attr.attachments.push(data);
            };

            this.renderAttachmentListView = function (data) {
                var currentHtml = this.select('attachmentListItem').html();
                var item = this.buildAttachmentListItem(data);
                this.select('attachmentListItem').append(item);
            };

            this.buildAttachmentListItem = function (attachment) {
                var attachmentData = {ident: attachment.ident,
                                      encoding: attachment.encoding,
                                      name: attachment.name,
                                      size: attachment.size,
                                      removable: true};

                var element = $(templates.compose.attachmentItem(attachmentData));
                var self = this;
                element.find('i.remove-icon').bind('click', function(event) {
                    var element = $(this);
                    var ident = element.closest('li').attr('data-ident');
                    self.trigger(document, events.mail.removeAttachment, {ident: ident, element: element});
                    event.preventDefault();
                });
                return element;
            };

            this.performPreUploadCheck = function(e, data) {
                if (data.originalFiles[0].size > ATTACHMENT_SIZE_LIMIT) {
                    return false;
                }

                return true;
            };

            this.removeUploadError = function() {
                var uploadError = this.select('uploadError');
                if (uploadError) {
                    uploadError.remove();
                }
            };

            this.showUploadError = function () {
                var self = this;

                var html = $(templates.compose.uploadAttachmentFailed());
                html.insertAfter(self.select('attachmentListItem'));

                self.on(self.select('closeIcon'), 'click', dismissUploadFailed);
                self.on(self.select('dismissButton'), 'click', dismissUploadFailed);
                self.on(self.select('uploadFileButton'), 'click', uploadAnotherFile);

                function dismissUploadFailed(event) {
                    event.preventDefault();
                    self.select('uploadError').remove();
                }

                function uploadAnotherFile(event) {
                    event.preventDefault();
                    self.trigger(document, events.mail.startUploadAttachment);
                }
            };

            this.showUploadProgressBar = function(e, data) {
                var element = $(templates.compose.attachmentUploadItem({
                    name: data.originalFiles[0].name,
                    size: data.originalFiles[0].size
                }));
                this.select('attachmentUploadItem').append(element);
                this.select('attachmentUploadItem').show();
            };

            this.hideUploadProgressBar = function() {
                this.select('attachmentUploadItem').hide();
                this.select('attachmentUploadItem').empty();
            };

            this.attachUploadAbort = function(e, data) {
                this.on(this.select('attachmentUploadItemAbort'), 'click', function(e) {
                    data.abort();
                    e.preventDefault();
                });
            };

            this.detachUploadAbort = function() {
                this.off(this.select('attachmentUploadItemAbort'), 'click');
            };

            this.addJqueryFileUploadConfig = function() {
                var self = this;

                self.removeUploadError();

                this.select('inputFileUpload').fileupload({
                    add: function(e, data) {
                        if (self.performPreUploadCheck(e, data)) {
                            self.showUploadProgressBar(e, data);
                            self.attachUploadAbort(e, data);
                            data.submit();
                        } else {
                            self.showUploadError();
                        }
                    },
                    url: self.attr.attachmentBaseUrl,
                    dataType: 'json',
                    done: function (e, response) {
                        self.detachUploadAbort();
                        self.hideUploadProgressBar();
                        self.trigger(document, events.mail.uploadedAttachment, response.result);
                    },
                    fail: function(e, data){
                        self.detachUploadAbort();
                        self.hideUploadProgressBar();
                        self.trigger(document, events.mail.failedUploadAttachment);
                    },
                    progressall: function (e, data) {
                        var progressRate = parseInt(data.loaded / data.total * 100, 10);
                        self.select('attachmentUploadItemProgress').css('width', progressRate + '%');
                    }
                }).bind('fileuploadstart', function (e) {
                    self.trigger(document, events.mail.uploadingAttachment);
                });
            };

            this.startUpload = function () {
                this.addJqueryFileUploadConfig();
                this.select('inputFileUpload').click();
            };

            this.removeAttachmentFromList = function(ident) {
              for (var i = 0; i < this.attr.attachments.length; i++) {
                if (this.attr.attachments[i].ident === ident) {
                  this.attr.attachments.remove(i);
                  break;
                }
              }
            };

            this.destroyAttachmentElement = function(element) {
              element.closest('li').remove();
            };

            this.removeAttachments = function(event, data) {
              this.removeAttachmentFromList(data.ident);
              this.destroyAttachmentElement(data.element);
            };

            this.after('initialize', function () {
                this.addJqueryFileUploadConfig();
                this.on(document, events.mail.uploadedAttachment, this.showAttachment);
                this.on(document, events.mail.startUploadAttachment, this.startUpload);
                this.on(document, events.mail.appendAttachment, this.addAttachment);
                this.on(document, events.mail.removeAttachment, this.removeAttachments);
            });
        }

        return attachmentList;
    });
