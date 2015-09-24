describeComponent('mail_view/data/feedback_sender', function () {
  'use strict';


  beforeEach(function () {
    this.setupComponent();
  });

  it('sends feedback with a POST to the server', function() {
    var data = {feedback: 'Pixelated is awesome!'};
    var feedbackSubmittedEventSpy = spyOnEvent(document, Pixelated.events.feedback.submitted);
    var deferred = $.Deferred();

    spyOn($, 'ajax').and.returnValue(deferred);

    this.component.trigger(document, Pixelated.events.feedback.submit, data);

    deferred.resolve();

    expect(feedbackSubmittedEventSpy).toHaveBeenTriggeredOn(document);

    expect($.ajax.calls.mostRecent().args[0]).toEqual('/feedback');
    expect($.ajax.calls.mostRecent().args[1].type).toEqual('POST');
    expect(JSON.parse($.ajax.calls.mostRecent().args[1].data)).toEqual(data);
  });

});
