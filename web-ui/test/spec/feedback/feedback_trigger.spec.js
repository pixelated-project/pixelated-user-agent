describeComponent('feedback/feedback_trigger', function () {
  'use strict';

  describe('Feedback link', function () {
   var features;

    beforeEach(function() {
      features = require('features');
    });

    it('Should provide feedback link if logout is enabled', function () {
      spyOn(features, 'isEnabled').and.returnValue(true);
      this.setupComponent('<nav id="feedback"></nav>', {});

      var feedback_link = this.component.$node.find('a')[0];
      expect(feedback_link).toExist();
    });

    it('Should not provide feedback link if disabled', function() {
      spyOn(features, 'isEnabled').and.returnValue(false);
      this.setupComponent('<nav id="feedback"></nav>', {});

      var feedback_link = this.component.$node.find('a')[0];
      expect(feedback_link).not.toExist();
    });

    it('Should trigger ui:feedback:open event on click', function () {

      this.setupComponent('<nav id="feedback"></nav>', {});
      var spy = spyOnEvent(document, Pixelated.events.dispatchers.rightPane.openFeedbackBox);

      this.$node.find('a').click();
      expect(spy).toHaveBeenTriggeredOn(document);
    });

  });
});

