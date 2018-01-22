var config = require('./webpack.config'),
    webpack = require('webpack'),
    path = require("path");
var BundleTracker = require('webpack-bundle-tracker')
var ExtractTextPlugin = require("extract-text-webpack-plugin");
var WebpackCleanupPlugin = require('webpack-cleanup-plugin');

// Output generated files in dist
config.output = {
  path: path.resolve('./dist/'),
  filename: "inks-[hash].js",
};

// Output stats in dist
config.plugins = [
  new BundleTracker({
    filename: './dist/webpack-stats.json',
  }),
  new ExtractTextPlugin({
    filename: "inks-[hash].css",
    allChunks: false,
  }),
  new WebpackCleanupPlugin({
    exclude : ['webpack-stats.json', ],
  }),
  new webpack.optimize.UglifyJsPlugin({
    minimize: true
  }),
  new webpack.DefinePlugin({
    'process.env': {
      NODE_ENV: '"production"'
    }
  })
];

module.exports = config;
