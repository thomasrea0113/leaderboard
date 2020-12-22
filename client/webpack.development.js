/* eslint-disable @typescript-eslint/no-var-requires */

const path = require('path');
const { merge } = require('webpack-merge');
const common = require('./webpack.common');

const config = merge(common, {
    mode: 'development',
    output: {
        publicPath: 'http://localhost:9000' + common.output.publicPath,
    },
    watch: true,
    devServer: {
        contentBase: path.join(__dirname, 'dist/bundles/'),
        port: 9000,
        clientLogLevel: 'warn',
        publicPath: common.output.publicPath,
        writeToDisk: true,
    },
});

module.exports = config;
