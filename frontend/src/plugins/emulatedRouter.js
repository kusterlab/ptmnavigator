
export default {
    install(Vue) {
        // Create a reactive router instance
        Vue.prototype.$router = new Vue({
            data() {
                return {
                    currentRoute: null
                }
            },
            methods: {
                push(route) {
                    this.currentRoute = route
                },
                replace(route) {
                    this.push(route)
                },
            }
        })

        // Make current route available as $route
        Vue.mixin({
            computed: {
                $route() {
                    return this.$router.currentRoute
                }
            }
        })
    }
}