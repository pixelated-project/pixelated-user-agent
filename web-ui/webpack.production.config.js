var path = require('path');
var webpack = require('webpack');
var copyWebpack = require('./config/copy-webpack');
var aliases = require('./config/alias-webpack');

module.exports = {
  entry: {
    app: './app/js/index.js',
    sandbox: './app/js/sandbox.js'
  },
  node: { fs: 'empty' },
  output: {
    path: path.join(__dirname, 'dist'),
    filename: '[name].js',
    publicPath: '/assets/'
  },
  resolve: {
    alias: aliases,
    extensions: ['', '.js']
  },
  module: {
    loaders: [
      {
        test: /\.js$/,
        loader: 'babel',
        query: { presets: ['es2015']}
      }
    ]
  },
  plugins: [
    new webpack.optimize.UglifyJsPlugin(),
    new webpack.optimize.DedupePlugin(),
    copyWebpack
  ]
}
