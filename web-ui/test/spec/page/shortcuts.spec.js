describeComponent('page/shortcuts', function () {
  'use strict';

  beforeEach(function () {
    this.setupComponent();
  });

  describe('shortcuts', function () {
    it('triggers openComposeBox when "c" is pressed and no input is focused', function () {
      var eventSpy = openComposeBoxEventSpy();

      $(document).trigger(keydownEvent(this.component.keyCodes.C));

      expect(eventSpy).toHaveBeenTriggeredOn(document)
    });

    it('does not trigger openComposeBox when "c" is pressed in an input field', function () {
      this.$node.append('<input type="text"/>');
      var eventSpy = openComposeBoxEventSpy();

      this.$node.find('input').trigger(keydownEvent(this.component.keyCodes.C));

      expect(eventSpy).not.toHaveBeenTriggeredOn(document)
    });

    it('does not trigger openComposeBox when "c" is pressed in a textarea', function () {
      this.$node.append('<textarea></textarea>');
      var eventSpy = openComposeBoxEventSpy();

      this.$node.find('textarea').trigger(keydownEvent(this.component.keyCodes.C));

      expect(eventSpy).not.toHaveBeenTriggeredOn(document)
    });

    it('triggers openNoMessageSelected when <Esc> is pressed', function () {
      var eventSpy = spyOnEvent(document, Pixelated.events.dispatchers.rightPane.openNoMessageSelected);

      $(document).trigger(keydownEvent(this.component.keyCodes.ESC));

      expect(eventSpy).toHaveBeenTriggeredOn(document)
    });

    it('triggers ui.mail.send when <Ctrl> + <Enter> is pressed', function () {
      var eventSpy = spyOnEvent(document, Pixelated.events.ui.mail.send);

      $(document).trigger(jQuery.Event('keydown', {ctrlKey: true, which: this.component.keyCodes.ENTER}));

      expect(eventSpy).toHaveBeenTriggeredOn(document)
    });


    it('triggers ui.mail.send when <Cmd>/<Meta> + <Enter> is pressed', function () {
      var eventSpy = spyOnEvent(document, Pixelated.events.ui.mail.send);

      $(document).trigger(jQuery.Event('keydown', {metaKey: true, which: this.component.keyCodes.ENTER}));

      expect(eventSpy).toHaveBeenTriggeredOn(document)
    });

    it('triggers search.focus when </> is pressed', function () {
      var eventSpy = spyOnEvent(document, Pixelated.events.search.focus);

      $(document).trigger(keydownEvent(this.component.keyCodes.FORWARD_SLASH));

      expect(eventSpy).toHaveBeenTriggeredOn(document)
    });

    it('triggers search.focus when <s> is pressed', function () {
      var eventSpy = spyOnEvent(document, Pixelated.events.search.focus);

      $(document).trigger(keydownEvent(this.component.keyCodes.S));

      expect(eventSpy).toHaveBeenTriggeredOn(document)
    });

    function openComposeBoxEventSpy() {
      return spyOnEvent(document, Pixelated.events.dispatchers.rightPane.openComposeBox);
    }

    function keydownEvent(code) {
      return jQuery.Event('keydown', {which: code});
    }
  });
});
