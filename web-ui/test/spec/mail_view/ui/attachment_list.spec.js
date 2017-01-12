describeMixin('mail_view/ui/attachment_list', function () {
    'use strict';

    describe('initialization', function () {
        beforeEach(function () {
            this.setupComponent('<div id="attachment-list">' +
                '<ul id="attachment-list-item"></ul>' +
                '<ul id="attachment-upload-item"></ul>' +
                '</div>');
        });

        it('should add attachment to the list based on uploadedAttachment event', function () {
            var stubAttachment = {ident: 'faked'};
            $(document).trigger(Pixelated.events.mail.appendAttachment, stubAttachment);
            expect(this.component.attr.attachments).toEqual([stubAttachment]);

            var anotherStubAttachment = {ident: 'faked 2'};
            $(document).trigger(Pixelated.events.mail.appendAttachment, anotherStubAttachment);
            expect(this.component.attr.attachments).toEqual([stubAttachment, anotherStubAttachment]);
        });

        it('should trigger add attachment event', function () {
            var triggerUploadAttachment = spyOnEvent(document, Pixelated.events.mail.appendAttachment);
            var stubAttachment = {ident: 'faked'};

            $(document).trigger(Pixelated.events.mail.uploadedAttachment, stubAttachment);

            expect(triggerUploadAttachment).toHaveBeenTriggeredOnAndWith(document, stubAttachment);
        });

        it('should render attachment list view based on uploadedAttachment event', function () {
            var stubAttachment = {ident: 'faked', name: 'haha.txt', size: 4500, encoding: 'base64'};

            $(document).trigger(Pixelated.events.mail.uploadedAttachment, stubAttachment);

            expect(this.component.select('attachmentListItem').html()).toContain('href="/attachment/faked');
            expect(this.component.select('attachmentListItem').html()).toContain('filename=haha.txt');
            expect(this.component.select('attachmentListItem').html()).toContain('encoding=base64');
            expect(this.component.select('attachmentListItem').html()).toContain('haha.txt');
            expect(this.component.select('attachmentListItem').html()).toContain('(4.39 Kb');
        });

        describe('Upload', function() {

            describe('Progress Bar', function () {
                it('should show/hide progress bar', function() {
                    this.component.showUploadProgressBar(null, {originalFiles: [{name: 'foo.txt', size: 4500}]});

                    expect(this.component.select('attachmentUploadItem').html()).toContain('foo.txt');
                    expect(this.component.select('attachmentUploadItem').html()).toContain('(4.39 Kb');
                    expect(this.component.select('attachmentUploadItem').css('display')).toEqual('block');

                    this.component.hideUploadProgressBar();

                    expect(this.component.select('attachmentUploadItem').css('display')).toEqual('none');
                });
            });

            describe('Cancel', function() {
                it('should cancel the upload', function() {
                    var fakeJQXHR = {
                        abort: function() {}
                    };
                    spyOn(fakeJQXHR, 'abort');
                    this.component.showUploadProgressBar(null, {originalFiles: [{name: 'foo.txt', size: 4500}]});
                    this.component.attachUploadAbort(null, fakeJQXHR);

                    this.component.select('attachmentUploadItemAbort').click();

                    expect(fakeJQXHR.abort).toHaveBeenCalled();
                });
            });

            describe('Error', function() {
                it('should show error message', function () {
                    this.component.showUploadError();

                    expect(this.component.select('uploadError').html()).toContain('Upload failed. This file exceeds the 1MB limit.');
                });

                it('should dismiss upload failed message when clicking close icon', function () {
                    this.component.showUploadError();

                    this.component.select('closeIcon').click();

                    expect(this.component.select('uploadError').html()).toBe(undefined);
                });

                it('should dismiss upload failed message when clicking dismiss button', function () {
                    this.component.showUploadError();

                    this.component.select('dismissButton').click();

                    expect(this.component.select('uploadError').html()).toBe(undefined);
                });

                it('should start file upload when clicking Choose another file button', function () {
                    this.component.showUploadError();
                    var triggerUploadAttachment = spyOnEvent(document, Pixelated.events.mail.startUploadAttachment);

                    this.component.select('uploadFileButton').click();

                    expect(triggerUploadAttachment).toHaveBeenTriggeredOn(document);
                });
            });

            describe('File size check', function (){
                var ONE_MEGABYTE = 1024*1024;
                var largeAttachment = {originalFiles: [{size: 5*ONE_MEGABYTE+1}]};

                it('should reject files larger than 5MB', function () {
                    var uploadAccepted = this.component.performPreUploadCheck(null, largeAttachment);
                    expect(uploadAccepted).toBe(false);
                });

                it('should accept files less or equal 5MB', function () {
                    var smallAttachment = {originalFiles: [{size: 5*ONE_MEGABYTE}]};
                    var uploadAccepted = this.component.performPreUploadCheck(null, smallAttachment);

                    expect(uploadAccepted).toBe(true);
                });
            });

            describe('Remove attachment', function () {
                it('should call the remove attachment method when triggered the removeAttachement event', function () {
                    var stubAttachment = {ident: 'whatever', element: 'element'};
                    spyOn(this.component, 'removeAttachmentFromList');
                    spyOn(this.component, 'destroyAttachmentElement');

                    $(document).trigger(Pixelated.events.mail.removeAttachment, stubAttachment);

                    expect(this.component.removeAttachmentFromList).toHaveBeenCalledWith('whatever');
                    expect(this.component.destroyAttachmentElement).toHaveBeenCalledWith('element');
                });

                it('should remove the attachment item from the DOM', function () {
                    var stubAttachment = {ident: 'whatever', element: 'element'};
                    this.setupComponent('<div id="attachment-list">' +
                        '<ul id="attachment-list-item"><li data-ident="whatever"><i class="remove-icon"></i></li></ul>' +
                        '<ul id="attachment-upload-item"></ul>' +
                        '</div>');

                    var element = this.component.$node.find('i.remove-icon');

                    expect(this.component.$node.find('li[data-ident=whatever]').length).toEqual(1);

                    this.component.destroyAttachmentElement(element);

                    expect(this.component.$node.find('li[data-ident=whatever]').length).toEqual(0);
                });


                it('should remove attachment from attachment list', function () {
                    var stubAttachment = {ident: 'whatever', element: 'element'};
                    this.component.attr.attachments = [{ident: 'whatever'}, {ident: 'another attachment'}];
                    this.component.removeAttachmentFromList('whatever');

                    expect(this.component.attr.attachments).toEqual([{ident: 'another attachment'}]);
                });


                it('when remove attachment that is not on the attachment list should not do anything', function () {
                    var stubAttachment = {ident: 'whatever', element: 'element'};
                    this.component.attr.attachments = [{ident: 'whatever'}];

                    this.component.removeAttachmentFromList({ident: 'different attachment'});

                    expect(this.component.attr.attachments).toEqual([{ident: 'whatever'}]);
                });
            });
        });
    });
});
