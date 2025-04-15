module.exports = {
    pages:{
        index: {
            entry:'src/main.js',
            title:'PTMNavigator'
        }
    },
    // Disable features we don't need for a library
    filenameHashing: false,
    productionSourceMap: false,
    css: {
        extract: false
    },

    chainWebpack: config => {
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
    // Configure the build properly for a library
    configureWebpack: {
        output: {
            libraryExport: 'default'
        },
        externals: {
            vue: {
                commonjs: 'vue',
                commonjs2: 'vue',
                amd: 'vue',
                root: 'Vue'
            },
            vuetify: {
                commonjs: 'vuetify',
                commonjs2: 'vuetify',
                amd: 'vuetify',
                root: 'Vuetify'
            }
        }
    },

}
