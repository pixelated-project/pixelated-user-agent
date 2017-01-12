var CopyWebpackPlugin = require('copy-webpack-plugin');

module.exports = new CopyWebpackPlugin([
  { context: 'app/', from: '404.html' },
  { context: 'app/', from: 'index.html' },
  { context: 'app/', from: 'sandbox.html' },
  { context: 'app/', from: 'css/*' },
  { context: 'app/', from: 'fonts/*' },
  { context: 'app/', from: 'locales/**/*' },
  { context: 'app/', from: 'bower_components/font-awesome/fonts/*' },
  {
    context: 'app/',
    from: 'bower_components/font-awesome/css/font-awesome.min.css',
    to: 'bower_components/font-awesome/css'
  },
  {
    context: 'app/',
    from: 'bower_components/jquery-file-upload/css/jquery.fileupload.css',
    to: 'bower_components/jquery-file-upload/css'
  },
  {
    context: 'app/',
    from: 'bower_components/modernizr/modernizr.js',
    to: 'bower_components/modernizr'
  },
  {
    context: 'app/',
    from: 'bower_components/lodash/dist/lodash.min.js',
    to: 'bower_components/lodash/dist'
  },
  {
    context: 'app/',
    from: 'bower_components/jquery/dist/jquery.min.js',
    to: 'bower_components/jquery/dist'
  },
  {
    context: 'app/',
    from: 'bower_components/jquery-ui/jquery-ui.min.js',
    to: 'bower_components/jquery-ui'
  },
  {
    context: 'app/',
    from: 'bower_components/jquery-file-upload/js/jquery.fileupload.js',
    to: 'bower_components/jquery-file-upload/js'
  },
  {
    context: 'app/',
    from: 'bower_components/handlebars/handlebars.min.js',
    to: 'bower_components/handlebars'
  },
  {
    context: 'app/',
    from: 'bower_components/typeahead.js/dist/typeahead.bundle.min.js',
    to: 'bower_components/typeahead.js/dist'
  },
  {
    context: 'app/',
    from: 'bower_components/iframe-resizer/js/iframeResizer.min.js',
    to: 'bower_components/iframe-resizer/js'
  },
  {
    context: 'app/',
    from: 'bower_components/iframe-resizer/js/iframeResizer.contentWindow.min.js',
    to: 'bower_components/iframe-resizer/js'
  },
  {
    context: 'app/',
    from: 'bower_components/foundation/js/foundation.js',
    to: 'bower_components/foundation/js'
  },
  {
    context: 'app/',
    from: 'bower_components/foundation/js/foundation/foundation.reveal.js',
    to: 'bower_components/foundation/js/foundation'
  },
  {
    context: 'app/',
    from: 'bower_components/foundation/js/foundation/foundation.offcanvas.js',
    to: 'bower_components/foundation/js/foundation'
  },
  {
    context: 'app/',
    from: 'js/foundation/initialize_foundation.js',
    to: 'js/foundation'
  }
])
