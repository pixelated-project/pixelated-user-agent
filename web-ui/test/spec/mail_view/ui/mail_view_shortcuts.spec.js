describeComponent('mail_view/ui/mail_view_shortcuts', function () {
  'use strict';

  beforeEach(function () {
    this.setupComponent();
  });

  describe('generic mail view shortcuts', function () {
    it('triggers openNoMessageSelected when [Esc] is pressed', function () {
      var eventSpy = spyOnEvent(document, Pixelated.events.dispatchers.rightPane.openNoMessageSelected);

      this.component.trigger(jQuery.Event('keydown', {which: this.component.keyCodes.ESC}));
      expect(eventSpy).toHaveBeenTriggeredOn(document);
    });
  });
});
