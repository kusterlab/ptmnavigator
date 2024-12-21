import Vue from 'vue';
import Router from 'vue-router';
import PTMNavigator from "@/components/PTMNavigator";


Vue.use(Router);

export default new Router({
    mode: 'history',
    //TODO: Check if this needs to be defined, else remove
    base: process.env.VUE_APP_ROUTER_BASE || '/',
    routes: [
        {
            path: '/',
            name: 'PTMNavigator',
            component: PTMNavigator
        }
    ],
    //TODO: Recommended by ChatGPT, no clue if this is correct
    install(app){
        app.component("PTMNavigator", PTMNavigator)
    }
});
