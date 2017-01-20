var path = require('path');
var HtmlWebpackPlugin = require('html-webpack-plugin');
var webpack = require('webpack');

module.exports = {
  entry: path.resolve(__dirname, './src/entry.jsx'),
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, '../bitsbox/frontend') + '/static'
  },
  devtool: 'eval-source-map',
  module: {
    loaders: [
      {
        test: /\.jsx?$/,
        exclude: /(node_modules|bower_components)/,
        loader: 'babel-loader',
        query: {
          presets: ['es2015', 'react'],
          plugins: ['react-relay']
        }
      },
      {
        test: /\.less$/,
        loader: 'style-loader!css-loader!less-loader'
      }
    ]
  },
  plugins: [
    // new webpack.optimize.UglifyJsPlugin(),
  ]
}
