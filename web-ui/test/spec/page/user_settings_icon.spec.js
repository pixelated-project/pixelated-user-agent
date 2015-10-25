describeComponent('page/user_settings_icon', function () {
    'use strict';

    describe('user settings icon', function () {
        it('shows the settings icon', function () {
            this.setupComponent('<nav id="user_settings_icon"></nav>', {});

            var settings_icon = this.component.$node.find('a')[0];
            expect(settings_icon).toExist();
        });
    });
});