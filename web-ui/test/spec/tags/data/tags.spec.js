/* global Pixelated */

describeComponent('tags/data/tags', function () {
  'use strict';

  var features;

  beforeEach( function () {
    features = require('features');
    spyOn(features, 'isAutoRefreshEnabled').and.returnValue(false);
    this.setupComponent();
  });

  it('asks the server for tags when receiving the tags:want event', function() {
    spyOn($, 'ajax').and.returnValue($.Deferred());

    this.component.trigger(Pixelated.events.tags.want);

    expect($.ajax.calls.mostRecent().args[0]).toEqual('/tags');
  });

  it('triggers an event on the initial sender after receiving tags', function() {
    var deferred = $.Deferred();

    spyOn($, 'ajax').and.returnValue(deferred);
    var me = {};
    var eventSpy = spyOnEvent(me, Pixelated.events.tags.received);

    this.component.trigger(Pixelated.events.tags.want, { caller: me});

    deferred.resolve(['foo', 'bar', 'quux/bar']);

    expect(eventSpy).toHaveBeenTriggeredOn(me);
  });

  it('triggers an event containing the returned tags', function() {
    var tags = ['foo', 'bar', 'quux/bar'];
    var deferred = $.Deferred();

    spyOn($, 'ajax').and.returnValue(deferred);
    var me = {};
    var eventSpy = spyOnEvent(me, Pixelated.events.tags.received);
    this.component.trigger(Pixelated.events.tags.want, { caller: me });

    deferred.resolve(tags);

    tags.push(this.component.all);
    expect(eventSpy.mostRecentCall.data).toEqual(jasmine.objectContaining({tags: tags}));
  });

  it('should reload taglist on mail sent', function(){
    spyOn($, 'ajax').and.returnValue($.Deferred());

    $(document).trigger(Pixelated.events.mail.sent);

    expect($.ajax.calls.mostRecent().args[0]).toEqual('/tags');
  });
});
