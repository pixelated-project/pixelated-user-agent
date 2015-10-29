describeComponent('page/user_settings_icon', function () {
  'use strict';

  beforeEach(function () {
    this.setupComponent();
  });

  it('toggles the user settings box when clicked', function () {
    var toggleEvent = spyOnEvent(document, Pixelated.events.ui.userSettingsBox.toggle);
    this.$node.click();
    expect(toggleEvent).toHaveBeenTriggeredOn(document);
  });
});
