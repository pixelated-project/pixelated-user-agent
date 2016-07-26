describeComponent('mail_view/ui/compose_box_shortcuts', function () {
  'use strict';

  beforeEach(function () {
    this.setupComponent();
  });

  describe('mail composition shortcuts', function () {
    it('triggers ui.mail.send when [Ctrl] + [Enter] is pressed', function () {
      var eventSpy = spyOnEvent(document, Pixelated.events.ui.mail.send);

      this.component.trigger(jQuery.Event('keydown', {ctrlKey: true, which: this.component.keyCodes.ENTER}));

      expect(eventSpy).toHaveBeenTriggeredOn(document);
    });

    it('triggers ui.mail.send when [Meta] + [Enter] is pressed', function () {
      var eventSpy = spyOnEvent(document, Pixelated.events.ui.mail.send);

      this.component.trigger(jQuery.Event('keydown', {metaKey: true, which: this.component.keyCodes.ENTER}));

      expect(eventSpy).toHaveBeenTriggeredOn(document);
    });
  });
});
