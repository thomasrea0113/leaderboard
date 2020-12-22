/* eslint-disable @typescript-eslint/no-var-requires */

const path = require('path');
const ESLintPlugin = require('eslint-webpack-plugin');
const BundleTracker = require('webpack-bundle-tracker');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');

const config = {
    entry: {
        site: path.resolve(__dirname, 'src/ts/site.ts'),
    },
    module: {
        rules: [
            {
                test: /\.ts$/,
                use: [
                    'babel-loader',
                    // we need to enable sourceMaps in the typescript compiler, and then load them
                    // directly prior to processing with babel, because the tsc compiler will remove
                    // empty lines, which won't be reflected in the source map if it is generated outside
                    // of tsc
                    'source-map-loader',
                    'ts-loader',
                ],
                exclude: /node_modules/,
            },
            {
                test: /\.scss$/,
                use: [MiniCssExtractPlugin.loader, 'css-loader', 'sass-loader'],
                exclude: /node_modules/,
            },
        ],
    },
    resolve: {
        extensions: ['.ts', '.js'],
    },
    output: {
        filename: '[name].[fullhash].js',
        path: path.resolve(__dirname, 'dist/bundles/'),
        publicPath: '/static/bundles/',
    },
    plugins: [
        new CleanWebpackPlugin(),
        new MiniCssExtractPlugin({ filename: '[name].[fullhash].css' }),
        new ESLintPlugin({ extensions: ['ts'] }),
        new BundleTracker({ filename: '../leaderboard/leaderboard/webpack-stats.json' }),
    ],
};

module.exports = config;
