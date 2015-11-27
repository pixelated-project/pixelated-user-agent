describeComponent('page/user_settings_box', function () {
  'use strict';

  var features;

  beforeEach(function () {
    this.setupComponent();
    features = require('features');
  });

  it('is extra high when the logout button is present', function() {
    spyOn(features, 'isLogoutEnabled').and.returnValue(true);

    expect(this.$node.hasClass('extra-bottom-space')).toBe(true);
  });

  it('toggles when receiving a toggle event', function () {
    expect(this.$node.hasClass('hidden')).toBe(false);
    this.component.trigger(document, Pixelated.events.ui.userSettingsBox.toggle);
    expect(this.$node.hasClass('hidden')).toBe(true);
    this.component.trigger(document, Pixelated.events.ui.userSettingsBox.toggle);
    expect(this.$node.hasClass('hidden')).toBe(false);
  });

  it('hides iteslf when the right arrow is clicked', function () {
    this.$node.removeClass('hidden');
    this.component.select('close').click();

    expect(this.$node.hasClass('hidden')).toBe(true);
  });
});
