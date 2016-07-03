// Karma configuration
//
// For all available config options and default values, see:
// http://karma-runner.github.io/0.10/config/configuration-file.html

module.exports = function (config) {
  'use strict';

  config.set({

    // base path, that will be used to resolve files and exclude
    basePath: '',

    // frameworks to use
    frameworks: ['jasmine-ajax', 'jasmine'],

    // list of files / patterns to load in the browser
    files: [
      // loaded without require
      'app/bower_components/lodash/dist/lodash.js',
      'app/bower_components/jquery/dist/jquery.js',
      'app/bower_components/jquery-ui/jquery-ui.min.js',
      'app/bower_components/jquery-file-upload/js/jquery.fileupload.js',
      'app/bower_components/jasmine-jquery/lib/jasmine-jquery.js',
      'app/bower_components/jasmine-flight/lib/jasmine-flight.js',
      'app/bower_components/jasmine-jquery/lib/jasmine-jquery.js',
      'app/bower_components/handlebars/handlebars.min.js',
      'app/bower_components/modernizr/modernizr.js',
      'app/bower_components/foundation/js/foundation.js',
      'app/bower_components/foundation/js/foundation/foundation.reveal.js',
      'app/bower_components/foundation/js/foundation/foundation.offcanvas.js',
      'app/js/lib/highlightRegex.js',

      // hack to load RequireJS after the shim libs
      'node_modules/requirejs/require.js',
      'node_modules/karma-requirejs/lib/adapter.js',

      // loaded with require
      {pattern: 'app/bower_components/DOMPurify/dist/purify.min.js', included: false},
      {pattern: 'app/bower_components/he/he.js', included: false},
      {pattern: 'app/bower_components/flight/**/*.js', included: false},
      {pattern: 'app/bower_components/i18next/**/*.js', included: false},
      {pattern: 'app/bower_components/i18next-xhr-backend/**/*.js', included: false},
      {pattern: 'app/bower_components/i18next-browser-languagedetector/**/*.js', included: false},
      {pattern: 'app/bower_components/quoted-printable/*.js', included: false},
      {pattern: 'app/bower_components/utf8/utf8.js', included: false},
      {pattern: 'app/locales/**/*.json', included: false},
      {pattern: 'app/js/**/*.js', included: false},
      {pattern: 'test/test_data.js', included: false},
      {pattern: 'test/custom_matchers.js', included: false},
      {pattern: 'test/features.js', included: false},
      {pattern: 'test/spec/**/*.spec.js', included: false},
      {pattern: 'app/sandbox.html', included: true, served: true},

      'test/test-main.js'
    ],

    proxies: {
        '/sandbox/sandbox.html': '/base/app/sandbox.html',
    },

    // list of files to exclude
    exclude: [
      'app/js/main.js'
    ],

    // test results reporter to use
    // possible values: 'dots', 'progress', 'junit', 'growl', 'coverage'
    reporters: ['dots', 'junit', 'coverage'],

    preprocessors: {
        'app/js/!(lib)/**/*.js': ['coverage']
    },

    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: true,

    // Start these browsers, currently available:
    // - Chrome
    // - ChromeCanary
    // - Firefox
    // - Opera
    // - Safari (only Mac)
    // - PhantomJS
    // - IE (only Windows)
    browsers: [
      'PhantomJS'
    ],

    // If browser does not capture in given timeout [ms], kill it
    captureTimeout: 5000,

    // Continuous Integration mode
    // if true, it capture browsers, run tests and exit
    singleRun: false,

    // Karma will report all the tests that are slower than given time limit (in
    // ms).
    reportSlowerThan: 1000,

    junitReporter: {
      outputFile: 'test-results.xml',
      suite: ''
    },

    coverageReporter: {
      type : 'html',
      dir : 'coverage/'
    }

  });
};
