describeComponent('page/shortcuts', function () {
  'use strict';

  describe('shortcuts', function () {
    it('triggers openComposeBox when "c" is pressed and no input is focused', function () {
      this.setupComponent();
      var eventSpy = openComposeBoxEventSpy();

      $(document).trigger(keypressEvent('c'));

      expect(eventSpy).toHaveBeenTriggeredOn(document)
    });

    it('does not trigger openComposeBox when "c" is pressed in an input field', function () {
      this.setupComponent();
      this.$node.append('<input type="text"/>');
      var eventSpy = openComposeBoxEventSpy();

      this.$node.find('input').trigger(keypressEvent('c'));

      expect(eventSpy).not.toHaveBeenTriggeredOn(document)
    });

    it('does not trigger openComposeBox when "c" is pressed in a textarea', function () {
      this.setupComponent();
      this.$node.append('<textarea></textarea>');
      var eventSpy = openComposeBoxEventSpy();

      this.$node.find('textarea').trigger(keypressEvent('c'));

      expect(eventSpy).not.toHaveBeenTriggeredOn(document)
    });

    function openComposeBoxEventSpy() {
      return spyOnEvent(document, Pixelated.events.dispatchers.rightPane.openComposeBox);
    }

    function keypressEvent(char) {
      return jQuery.Event('keypress', {which: char.charCodeAt(0)});
    }
  });
});
