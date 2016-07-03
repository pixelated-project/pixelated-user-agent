describeComponent('mail_view/ui/feedback_box', function () {
  'use strict';
  var feedbackCache;

  beforeEach(function () {
    feedbackCache = require('feedback/feedback_cache');
    Pixelated.mockBloodhound();
    this.setupComponent('<div></div>');
  });


  describe('close button behavior', function () {

    it('should fire Show no message selected if the close button is clicked', function () {
      var spy = spyOnEvent(document, Pixelated.events.dispatchers.rightPane.openNoMessageSelected);
      this.component.select('closeButton').click();
      expect(spy).toHaveBeenTriggeredOn(document);
    });

  });

  describe('caching feedback data', function () {
    it('should cache textbox feedback data', function () {
      this.component.select('textBox').val('Pixelated is Awesome!');
      this.component.select('textBox').trigger("change");
      expect(feedbackCache.getCache()).toEqual('Pixelated is Awesome!');
    });

    it('should have its textbox feedback field, filled with feedbackCache value, when setup', function(){
      feedbackCache.setCache("foo bar");

      this.setupComponent('<div></div>');
      expect(this.component.select('textBox').val()).toEqual('foo bar');
    });


  });

  describe('when submit feedback', function () {

    it('should fire submit feedback event', function () {
      var spy = spyOnEvent(document, Pixelated.events.feedback.submit);

      this.component.select('textBox').val('Pixelated is Awesome!');
      this.component.select('submitButton').click();
      expect(spy).toHaveBeenTriggeredOnAndWith(document, {feedback: 'Pixelated is Awesome!'});
    });

    it('should close feedback box after submit', function () {
      var spy = spyOnEvent(document, Pixelated.events.dispatchers.rightPane.openNoMessageSelected);

      this.component.trigger(document, Pixelated.events.feedback.submitted);
      expect(spy).toHaveBeenTriggeredOn(document);
      expect(feedbackCache.getCache()).toEqual('');
    });

    it('should shows success message after submit', function () {
      var spy = spyOnEvent(document, Pixelated.events.ui.userAlerts.displayMessage);

      this.component.trigger(document, Pixelated.events.feedback.submitted);
      expect(spy).toHaveBeenTriggeredOnAndWith(document, {message: 'Thanks for your feedback!'});
    });

  });

});
