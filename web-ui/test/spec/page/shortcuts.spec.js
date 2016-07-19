describeComponent('page/shortcuts', function () {
  'use strict';

  beforeEach(function () {
    this.setupComponent();
  });

  describe('global shortcuts', function () {
    it('triggers openNoMessageSelected when [Esc] is pressed', function () {
      var eventSpy = spyOnEvent(document, Pixelated.events.dispatchers.rightPane.openNoMessageSelected);

      $(document).trigger(keydownEvent(this.component.keyCodes.ESC));

      expect(eventSpy).toHaveBeenTriggeredOn(document)
    });
  });

  describe('mail list shortcuts', function () {
    function shortcutEventAndTriggeredEventSpy() {
      return [
        {
          eventSpy: openComposeBoxEventSpy(),
          shortcutEvent: keydownEvent(this.component.keyCodes.C)
        },
        {
          eventSpy: spyOnEvent(document, Pixelated.events.search.focus),
          shortcutEvent: keydownEvent(this.component.keyCodes.FORWARD_SLASH)
        },
        {
          eventSpy: spyOnEvent(document, Pixelated.events.search.focus),
          shortcutEvent: keydownEvent(this.component.keyCodes.S)
        }
      ]
    }

    it('are triggered when no input or textarea is focused', function () {
      shortcutEventAndTriggeredEventSpy.call(this).forEach(function (args) {
        var eventSpy = args.eventSpy;

        $(document).trigger(args.shortcutEvent);

        expect(eventSpy).toHaveBeenTriggeredOn(document);
      });
    });

    it('are not triggered when an input is focused', function () {
      var self = this;
      shortcutEventAndTriggeredEventSpy.call(this).forEach(function (args) {
        self.$node.append('<input />');
        var eventSpy = args.eventSpy;

        self.$node.find('input').trigger(args.shortcutEvent);

        expect(eventSpy).not.toHaveBeenTriggeredOn(document);
      });
    });

    it('are not triggered when a textarea is focused', function () {
      var self = this;
      shortcutEventAndTriggeredEventSpy.call(this).forEach(function (args) {
        self.$node.append('<textarea></textarea>');
        var eventSpy = args.eventSpy;

        self.$node.find('textarea').trigger(args.shortcutEvent);

        expect(eventSpy).not.toHaveBeenTriggeredOn(document);
      });
    });

    it('are not triggered when the composeBox is opened', function () {
      var self = this;
      shortcutEventAndTriggeredEventSpy.call(this).forEach(function (args) {
        addComposeBox.call(self);
        var eventSpy = args.eventSpy;

        $(document).trigger(args.shortcutEvent);

        expect(eventSpy).not.toHaveBeenTriggeredOn(document);
      });
    });
  });

  describe('mail composition shortcuts', function () {
    it('triggers ui.mail.send when [Ctrl] + [Enter] is pressed and compose box is open', function () {
      addComposeBox.call(this);
      var eventSpy = spyOnEvent(document, Pixelated.events.ui.mail.send);

      $(document).trigger(jQuery.Event('keydown', {ctrlKey: true, which: this.component.keyCodes.ENTER}));

      expect(eventSpy).toHaveBeenTriggeredOn(document)
    });

    it('triggers ui.mail.send when [Meta] + [Enter] is pressed and compose box is open', function () {
      addComposeBox.call(this);
      var eventSpy = spyOnEvent(document, Pixelated.events.ui.mail.send);

      $(document).trigger(jQuery.Event('keydown', {metaKey: true, which: this.component.keyCodes.ENTER}));

      expect(eventSpy).toHaveBeenTriggeredOn(document)
    });

    it('does not trigger ui.mail.send when [Ctrl] + [Enter] is pressed and compose box is closed', function () {
      var eventSpy = spyOnEvent(document, Pixelated.events.ui.mail.send);

      $(document).trigger(jQuery.Event('keydown', {ctrlKey: true, which: this.component.keyCodes.ENTER}));

      expect(eventSpy).not.toHaveBeenTriggeredOn(document)
    });

    it('does not trigger ui.mail.send when [Meta] + [Enter] is pressed and compose box is closed', function () {
      var eventSpy = spyOnEvent(document, Pixelated.events.ui.mail.send);

      $(document).trigger(jQuery.Event('keydown', {metaKey: true, which: this.component.keyCodes.ENTER}));

      expect(eventSpy).not.toHaveBeenTriggeredOn(document)
    });
  });

  function openComposeBoxEventSpy() {
    return spyOnEvent(document, Pixelated.events.dispatchers.rightPane.openComposeBox);
  }

  function keydownEvent(code) {
    return jQuery.Event('keydown', {which: code});
  }

  function addComposeBox() {
    this.$node.append($('<div>', {id: this.component.composeBoxId}));
  }
});
