
var tests = Object.keys(window.__karma__.files).filter(function (file) {
  'use strict';
  return (/\.spec\.js$/.test(file));
});

beforeEach(function() {
    'use strict';
    jasmine.Ajax.install();
});

afterEach(function() {
    'use strict';
    jasmine.Ajax.uninstall();
});

requirejs.config({

  baseUrl: '/base',

  paths: {
    'page': 'app/js/page',
    'js': 'app/js',
    'lib': 'app/js/lib',
    'hbs': 'app/js/generated/hbs',
    'flight': 'app/bower_components/flight',
    'DOMPurify': 'app/bower_components/DOMPurify/dist/purify.min',
    'he': 'app/bower_components/he/he',
    'views': 'app/js/views',
    'helpers': 'app/js/helpers',
    'feedback': 'app/js/feedback',
    'tags': 'app/js/tags',
    'mail_list': 'app/js/mail_list',
    'mail_list_actions': 'app/js/mail_list_actions',
    'user_alerts': 'app/js/user_alerts',
    'mail_view': 'app/js/mail_view',
    'dispatchers': 'app/js/dispatchers',
    'mixins': 'app/js/mixins',
    'services': 'app/js/services',
    'search': 'app/js/search',
    'monkey_patching': 'app/js/monkey_patching',
    'i18next': 'app/bower_components/i18next/i18next',
    'i18nextXHRBackend': 'app/bower_components/i18next-xhr-backend/i18nextXHRBackend',
    'i18nextBrowserLanguageDetector': 'app/bower_components/i18next-browser-languagedetector/i18nextBrowserLanguageDetector',
    'quoted-printable': 'app/bower_components/quoted-printable',
    'utf8': 'app/bower_components/utf8',
    'test': 'test',
    'features': 'test/features',
    'user_settings': 'app/js/user_settings'
  },

  deps: tests,

  callback: function () {
    'use strict';
    require(['page/events','test/test_data', 'views/i18n', 'i18next', 'i18nextXHRBackend', 'monkey_patching/array', 'views/recipientListFormatter', 'test/custom_matchers'],
      function (events, testData, i18n, i18next, i18n_backend, mp, recipientListFormatter, customMatchers) {
      window.Pixelated = window.Pixelated || {};
      window.Pixelated.events = events;
      window.Pixelated.testData = testData;
      window.Pixelated.mockBloodhound = function() {
        window.Bloodhound = function() {};
        window.Bloodhound.prototype.initialize = function() {};
        window.Bloodhound.prototype.ttAdapter = function() {};
        window.Bloodhound.prototype.clear = function() {};
        window.Bloodhound.prototype.clearPrefetchCache = function() {};
        window.Bloodhound.prototype.clearRemoteCache = function() {};
        $.fn.typeahead = function() {};
      };

      i18next
      .use(i18n_backend)
      .init({
        lng: 'en_US',
        backend: {
          loadPath: '/base/app/locales/en_US/translation.json'
        }
      });
      Handlebars.registerHelper('t', i18n.t);

      i18next.on('loaded', function() {
        window.__karma__.start();
      });
    });
  }
});
