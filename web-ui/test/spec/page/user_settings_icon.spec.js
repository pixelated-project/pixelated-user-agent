describeComponent('page/user_settings_icon', function () {
    'use strict';

    describe('user settings icon', function () {
        var features;

        beforeEach(function() {
            features = require('features');
        });

        it('should provide settings icon if logout is enabled', function () {
            spyOn(features, 'isLogoutEnabled').and.returnValue(true);

            this.setupComponent('<nav id="user_settings_icon"></nav>', {});

            var settings_icon = this.component.$node.find('a')[0];
            expect(settings_icon).toExist();
        });

        it('should also provite settings icon link if logout is disabled', function() {
            spyOn(features, 'isLogoutEnabled').and.returnValue(false);

            this.setupComponent('<nav id="user_settings_icon"></nav>', {});

            var settings_icon = this.component.$node.find('a')[0];
            expect(settings_icon).toExist();
        });
    });
});