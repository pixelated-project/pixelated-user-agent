describeComponent('mail_view/ui/mail_view', function () {
  'use strict';

  var mail;

  var testData;

  beforeEach(function () {
    mail = {ident: 1, header: { date: '12/12/12T12:12' }, tags: ['inbox']};
    testData = {mail: Pixelated.testData().parsedMail.simpleTextPlain};
    Pixelated.mockBloodhound();
    this.setupComponent('<div></div>', {mail: mail});
  });

  it('triggers mail:want on ui:openMail', function () {
    var spyEvent = spyOnEvent(document, Pixelated.events.mail.want);

    this.setupComponent('<div></div>', {ident: mail.ident });

    expect(spyEvent).toHaveBeenTriggeredOn(document);
    expect(spyEvent.mostRecentCall.data.mail).toEqual(1);
  });

  it('triggers mail.highlightMailContent when receiving mail.here', function () {
    var hightlightEvent = spyOnEvent(document,Pixelated.events.mail.highlightMailContent);
    this.component.trigger(this.component, Pixelated.events.mail.here);
    expect(hightlightEvent).toHaveBeenTriggeredOn(document);
  });

  it('triggers dispatchers.rightPane.openNoMessageSelected when getting mail.notFound', function () {
    var openNoMessageSelectedEvent = spyOnEvent(document, Pixelated.events.dispatchers.rightPane.openNoMessageSelected);

    this.component.trigger(this.component, Pixelated.events.mail.notFound);

    expect(openNoMessageSelectedEvent).toHaveBeenTriggeredOn(document);
  });

  it('removes the tag from the mail when the tag label is clicked', function() {
    var updateSpy = spyOnEvent(document, Pixelated.events.mail.tags.update);

    testData.mail.tags = ['inbox', 'other'];
    this.component.displayMail({}, testData);
    this.component.removeTag('inbox');

    expect(updateSpy).toHaveBeenTriggeredOn(document);
    expect(updateSpy.mostRecentCall.data.tags).toEqual(['other']);
  });

  it('removes the tag from email even if tag is highlighted', function () {
    var updateSpy = spyOnEvent(document, Pixelated.events.mail.tags.update);

    testData.mail.tags = ['tag', 'other'];
    this.component.displayMail({}, testData);

    var inboxTag = this.component.$node.find('.mail-read-view__header-tags-tag[data-tag="tag"]');
    inboxTag.html('<em class="search-highlight">' + inboxTag.text() + '</em>');
    this.component.$node.find('.search-highlight').click();

    expect(updateSpy).toHaveBeenTriggeredOn(document);
    expect(updateSpy.mostRecentCall.data.tags).toEqual(['other']);
  });

  it('removes numeric tag from the mail when its label is clicked', function() {
    var updateSpy = spyOnEvent(document, Pixelated.events.mail.tags.update);

    testData.mail.tags = ['inbox', '12345'];
    this.component.displayMail({}, testData);
    this.component.removeTag(12345);

    expect(updateSpy).toHaveBeenTriggeredOn(document);
    expect(updateSpy.mostRecentCall.data.tags).toEqual(['inbox']);
  });

  it('remove tag triggers refreshTagList event', function(){
    var refreshTagListEvent = spyOnEvent(document, Pixelated.events.dispatchers.tags.refreshTagList);
    this.component.displayMail({}, testData);
    this.component.removeTag('inbox');
    expect(refreshTagListEvent).toHaveBeenTriggeredOn(document);
  });

  it('verifies if new tag input is hidden when rendering mail view', function() {
    this.component.displayMail({}, testData);

    var newTagInputComponent = this.component.select('newTagInput');
    expect(newTagInputComponent.attr('style').trim()).toEqual('display: none;');
  });

  it('verifies if new tag input is shown when clicking on new tag button', function() {
    this.component.displayMail({}, testData);

    var newTagInputComponent = this.component.select('newTagInput');

    this.component.select('newTagButton').click();

    expect(newTagInputComponent.attr('style').trim()).not.toEqual('display: none;');
  });

  it('hides new tag input when pressing esc key', function(){
    this.component.displayMail({}, testData);
    this.component.select('newTagButton').click();

    var e = creatingEvent('keydown', 27);
    var newTagInputComponent = this.component.select('newTagInput');

    newTagInputComponent.trigger(e);

    expect(newTagInputComponent.attr('style').trim()).toEqual('display: none;');
  });

  it('assumes that the mail is encrypted and valid if at least one of the locks are valid', function() {
    var email = testData;
    email.security_casing = {locks: [{state: 'valid'}, {state: 'failure'}]};
    expect(this.component.checkEncrypted(email).cssClass).toEqual('security-status__label--encrypted');
  });

  it('assumes that the mail is encrypted and failure if all the locks are failed', function() {
    var email = testData;
    email.security_casing = {locks: [{state: 'failure'}, {state: 'failure'}]};
    expect(this.component.checkEncrypted(email).cssClass).toEqual('security-status__label--encrypted--with-error');
  });

  it('assumes that the mail is not encrypted if it doesn\'t have any locks', function() {
    var email = testData;
    email.security_casing = {locks: []};
    expect(this.component.checkEncrypted(email).cssClass).toEqual('security-status__label--not-encrypted');
  });

  it('assumes that the mail is signed only if all imprints are valid', function() {
    var email = testData;
    email.security_casing = {imprints: [{state: 'valid', seal: {trust: 'marginal', validity: 'marginal'}}, {state: 'valid', seal: {trust: 'marginal', validity: 'marginal'}}]};
    expect(this.component.checkSigned(email).cssClass).toEqual('security-status__label--signed');
  });

  it('assumes that the mail is signed with failures if there is a revoke or expire', function() {
    var email = testData;
    email.security_casing = {imprints: [{state: 'valid', seal: {trust: 'marginal', validity: 'marginal'}}, {state: 'from_revoked', seal: {trust: 'marginal', validity: 'marginal'}}]};
    expect(this.component.checkSigned(email).cssClass).toEqual('security-status__label--signed--revoked');
  });

  it('assumes that mail is not trusted if its signature contains no_trust from the user', function() {
    var email = testData;
    email.security_casing = {imprints: [{seal: {trust: 'no_trust', validity: 'ultimate'}}]};
    expect(this.component.checkSigned(email).cssClass).toEqual('security-status__label--signed--not-trusted');
  });

  it('uses validity when trust is not present', function() {
    var email = testData;
    email.security_casing = {imprints: [{seal: { validity: 'no_trust'}}]};
    expect(this.component.checkSigned(email).cssClass).toEqual('security-status__label--signed--not-trusted');
  });

  it('assumes not trusted when the signature is not found', function(){
    var email = testData;
    email.security_casing = {imprints: [{seal: null}]};
    expect(this.component.checkSigned(email).cssClass).toEqual('security-status__label--signed--not-trusted');
  });

  it('assumes that the mail is not signed if there are no imprints', function() {
    var email = testData;
    email.security_casing = {imprints: []};
    expect(this.component.checkSigned(email).cssClass).toEqual('security-status__label--not-signed');
  });

  it('assumes that there is no signature info to show', function() {
    var email = testData;
    email.security_casing = {imprints: [{state: 'no_signature_information'}]};
    expect(this.component.checkSigned(email).cssClass).toEqual('security-status__label--not-signed');
  });

  it('shows that mail is encrypted if it is', function() {
    spyOn(this.component, 'checkEncrypted').and.returnValue({cssClass: 'security-status__label--encrypted'});
    this.component.displayMail({}, testData);
    expect(this.component.$node.find('.security-status__label--encrypted')).toExist();
  });

  it('shows that mail is signed if it is', function() {
    spyOn(this.component, 'checkSigned').and.returnValue({cssClass: 'security-status__label--signed'});
    this.component.displayMail({}, testData);
    expect(this.component.$node.find('.security-status__label--signed')).toExist();
  });

  it('shows that mail is not encrypted if it isn\'t', function() {
    spyOn(this.component, 'checkEncrypted').and.returnValue({cssClass: 'security-status__label--not-encrypted'});
    this.component.displayMail({}, testData);
    expect(this.component.$node.find('.security-status__label--not-encrypted')).toExist();
  });

  it('shows that mail is not signed if it isn\'t', function() {
    spyOn(this.component, 'checkEncrypted').and.returnValue({cssClass: 'securty-status__label--not-signed'});
    this.component.displayMail({}, testData);
    expect(this.component.$node.find('.security-status__label--not-signed')).toExist();
  });

  it('creates new tag when pressing Enter key on new tag input', function(){
    var tagsUpdateEvent = spyOnEvent(document, Pixelated.events.mail.tags.update);

    this.component.displayMail({}, testData);
    this.component.select('newTagButton').click();

    var newTagInputComponent = this.component.select('newTagInput');
    newTagInputComponent.val('Test');

    var e = creatingEvent('keydown', 13); //ENTER KEY EVENT
    newTagInputComponent.trigger(e);

    var tags = testData.mail.tags.slice();
    tags.push('Test');
    expect(tagsUpdateEvent).toHaveBeenTriggeredOnAndWith(document, { ident: testData.mail.ident, tags: tags});
  });

  it('creates new tag when pressing Enter key on new tag input', function(){
    var tagsUpdateEvent = spyOnEvent(document, Pixelated.events.mail.tags.update);

    this.component.displayMail({}, testData);
    this.component.select('newTagButton').click();

    var newTagInputComponent = this.component.select('newTagInput');
    newTagInputComponent.val('    ');

    var e = creatingEvent('keydown', 13); //ENTER KEY EVENT
    newTagInputComponent.trigger(e);

    expect(tagsUpdateEvent).not.toHaveBeenTriggeredOnAndWith(document);
  });

  it('trigger mail delete event when moving email to trash', function(){
    var mailDeleteEvent = spyOnEvent(document, Pixelated.events.ui.mail.delete);

    Foundation.global.namespace = '';
    $(document).foundation();

    this.component.displayMail({}, testData);
    this.component.moveToTrash();

    expect(mailDeleteEvent).toHaveBeenTriggeredOnAndWith(document, { mail: this.component.attr.mail });
  });

  it('shows no message selected pane when deleting the email being composed', function() {
    var openNoMessageSelectedPaneEvent = spyOnEvent(document, Pixelated.events.dispatchers.rightPane.openNoMessageSelected);
    var mails = [{ident: 123}];
    this.component.attr.mail = mails[0];

    this.component.trigger(document, Pixelated.events.mail.deleted, {mails: mails});

    expect(openNoMessageSelectedPaneEvent).toHaveBeenTriggeredOn(document);
  });

  it('does not show no message selected pane when deleting a different set of emails', function() {
    var openNoMessageSelectedPaneEvent = spyOnEvent(document, Pixelated.events.dispatchers.rightPane.openNoMessageSelected);
    var mails = [{ident: 321}];
    this.component.attr.mail = {ident: 123};

    this.component.trigger(document, Pixelated.events.mail.deleted, {mails: mails});

    expect(openNoMessageSelectedPaneEvent).not.toHaveBeenTriggeredOn(document);
  });

  it('opens the no message selected pane when clicking the close button', function() {
    var openNoMessageSelectedEvent = spyOnEvent(document, Pixelated.events.dispatchers.rightPane.openNoMessageSelected);

    this.component.displayMail({}, testData);
    this.component.select('closeMailButton').click();

    expect(openNoMessageSelectedEvent).toHaveBeenTriggeredOn(document);
  });

  it('shows a download link for attachments', function() {
    var withAttachments = {mail: Pixelated.testData().parsedMail.withAttachments};

    this.component.displayMail({}, withAttachments);

    var attachmentLink = $(this.component.$node.find('.mail-read-view__attachments-item').html());
    var expectedLink = '/attachment/912ec803b2ce49e4a541068d495ab570?content_type=text/plain&encoding=base64&filename=filename.txt';
    expect(attachmentLink.attr('href')) .toBe(expectedLink);
  });

  function creatingEvent(event, keyCode) {
    var e = $.Event(event);
    e.which = keyCode;
    return e;
  }
});
