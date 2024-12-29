const {defineConfig} = require('@vue/cli-service')
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
    outputDir: 'dist',
    // Recommended by ChatGPT, no clue if this is correct
    // configureWebpack: {
    //     output: {
    //         libraryExport: 'default'
    //     },
    // },
    // relative to outputDir
    assetsDir: 'static',

})

