const path = require('path');
const UglifyJsPlugin = require('uglifyjs-webpack-plugin');
const uglifyOptions = require('./uglifyOptions')

module.exports = {
  entry: './src/script.js',
  output: {
    filename: 'main.js',
    path: path.resolve(__dirname, 'dist')
  },
  optimization: {
      minimizer: [
        new UglifyJsPlugin(uglifyOptions())
      ]
    }
};
