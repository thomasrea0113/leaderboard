module.exports = {
    presets: [
        [
            '@babel/preset-env',
            {
                targets: {
                    edge: '17',
                    firefox: '60',
                    chrome: '67',
                    safari: '11.1',
                },
                useBuiltIns: 'usage',
                corejs: '2.6.12',
            },
        ],
    ],
    plugins: ['@babel/plugin-transform-arrow-functions'],
};
