/* eslint-disable @typescript-eslint/no-var-requires */

const path = require('path');
const ESLintPlugin = require('eslint-webpack-plugin');
const BundleTracker = require('webpack-bundle-tracker');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');

const bundlePath = 'bundles/';

const config = {
    entry: {
        site: path.resolve(__dirname, 'src/ts/site.ts'),
    },
    module: {
        rules: [
            {
                test: /\.ts$/,
                use: ['babel-loader', 'ts-loader'],
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
        publicPath: '/' + bundlePath,
    },
    plugins: [
        new CleanWebpackPlugin(),
        new MiniCssExtractPlugin({ filename: '[name].[fullhash].css' }),
        new ESLintPlugin(),
        new BundleTracker({ filename: 'webpack-stats.json' }),
    ],
};

module.exports = config;
