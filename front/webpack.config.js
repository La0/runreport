var path = require("path")
var webpack = require('webpack')
var BundleTracker = require('webpack-bundle-tracker')
var ExtractTextPlugin = require("extract-text-webpack-plugin");


module.exports = {
  context: __dirname,

  entry: './js/app.js',

  output: {
      path: path.resolve('./bundles/'),
      filename: "runreport-[hash].js",
  },

  plugins: [
    new BundleTracker({filename: './webpack-stats.json'}),
    new ExtractTextPlugin({
      filename: "runreport-[hash].css",
      allChunks: false,
    }),
  ],

  module: {
    rules: [
      {
        test: /\.css$/,
        use: ExtractTextPlugin.extract({
          fallback: "style-loader",
          use: "css-loader"
        })
      },
      {
        test: /\.scss|sass$/,
        use: ExtractTextPlugin.extract({
          fallback: "style-loader",
          use: [{
            loader: 'css-loader', // translates CSS into CommonJS modules
          }, {
            loader: 'postcss-loader', // Run post css actions
            options: {
              plugins: function () { // post css plugins, can be exported to postcss.config.js
                return [
                  require('precss'),
                  require('autoprefixer')
                ];
              }
            }
          }, {
            loader: 'sass-loader' // compiles Sass to CSS
          }]
        })
      },
      //{
      //  test: /\.less$/,
      //  use: ExtractTextPlugin.extract({
      //    fallback: "style-loader",
      //    use: "css-loader!less-loader"
      //  })
      //},
      {
        test: /\.(png|jpg|jpeg)$/,
        use: 'file-loader?name=images/[name].[ext]'
      },
      {
        test: /\.(eot|svg|ttf|woff|woff2|otf)/,
        use: 'file-loader?name=fonts/[name].[ext]'
      },
      {
        // Vue components
        test: /\.vue$/,
        use: 'vue-loader'
      },
    ]
  },

  resolve: {
    modules: [
      path.join(__dirname, "node_modules"),
      path.join(__dirname),
    ],
    extensions: ['.js', '.vue', '.css', '.json'],
    alias: {
      'vue': 'vue/dist/vue.esm.js', // Use lighter runtime
    },
  },
}
