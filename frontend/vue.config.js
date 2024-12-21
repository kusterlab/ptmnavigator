const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({

    chainWebpack: config => {
        config
            .plugin('html')
            .tap(args => {
                args[0].title = 'PTMNavigator'
                return args
            })

        config.module
            .rule('css-for-svgs')
            .test(/\.css.prdb$/)
            .use('file-loader')
            .loader('file-loader')
            .options({
                name: 'css/[name].[contenthash].css',
                esModule: false
            })
            .end()
    },


        transpileDependencies: [
        'vuetify'
    ],
    outputDir: '../dist',

    // relative to outputDir
    assetsDir: 'static',

    //TODO: Check if this needs to be defined, else remove
    publicPath: process.env.VUE_APP_ROUTER_BASE,
})

