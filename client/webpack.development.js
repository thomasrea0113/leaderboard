/* eslint-disable @typescript-eslint/no-var-requires */

const { merge } = require('webpack-merge');
const common = require('./webpack.common');

const config = merge(common, {
    mode: 'development',
    watch: true,
    devtool: 'inline-source-map',
});

module.exports = config;
