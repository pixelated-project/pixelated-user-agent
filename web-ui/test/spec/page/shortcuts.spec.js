describeComponent('page/shortcuts', function () {
  'use strict';

  beforeEach(function () {
    this.setupComponent();
  });

  describe('mail list shortcuts', function () {
    function shortcutEventAndTriggeredEventSpy() {
      return [
        {
          eventSpy: spyOnEvent(document, Pixelated.events.dispatchers.rightPane.openComposeBox),
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
      ];
    }

    it('are triggered when no input or textarea is focused', function () {
      _.each(shortcutEventAndTriggeredEventSpy.call(this), function (args) {
        var eventSpy = args.eventSpy;

        this.component.trigger(args.shortcutEvent);

        expect(eventSpy).toHaveBeenTriggeredOn(document);
      }, this);
    });

    it('are not triggered when an input is focused', function () {
      _.each(shortcutEventAndTriggeredEventSpy.call(this), function (args) {
        this.$node.append('<input />');
        var eventSpy = args.eventSpy;

        this.$node.find('input').trigger(args.shortcutEvent);

        expect(eventSpy).not.toHaveBeenTriggeredOn(document);
      }, this);
    });

    it('are not triggered when a textarea is focused', function () {
      _.each(shortcutEventAndTriggeredEventSpy.call(this), function (args) {
        this.$node.append('<textarea></textarea>');
        var eventSpy = args.eventSpy;

        this.$node.find('textarea').trigger(args.shortcutEvent);

        expect(eventSpy).not.toHaveBeenTriggeredOn(document);
      }, this);
    });

    it('are not triggered when the composeBox is opened', function () {
      _.each(shortcutEventAndTriggeredEventSpy.call(this), function (args) {
        addComposeBox.call(this);
        var eventSpy = args.eventSpy;

        this.component.trigger(args.shortcutEvent);

        expect(eventSpy).not.toHaveBeenTriggeredOn(document);
      }, this);
    });
  });

  function keydownEvent(code) {
    return jQuery.Event('keydown', {which: code});
  }

  function addComposeBox() {
    this.$node.append($('<div>', {id: this.component.composeBoxId}));
  }
});
