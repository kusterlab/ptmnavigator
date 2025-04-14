import Vue from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify';
import vueCookie from 'vue-cookie'
import router from './router';
import 'vuetify/dist/vuetify.min.css';
import 'material-design-icons-iconfont/dist/material-design-icons.css'
// import PTMNavigator from "@/components/PTMNavigator";
import PTMNavigator from './components/PTMNavigator.vue';
import 'devextreme/dist/css/dx.common.css'
import 'devextreme/dist/css/dx.material.blue.light.compact.css'


Vue.use(vueCookie)

Vue.config.productionTip = false

const PTMNavigatorPlugin = {
  install(Vue) {
    Vue.component("ptm-navigator", PTMNavigator)
  }
}
// Make both available for different import styles
PTMNavigatorPlugin.PTMNavigator = PTMNavigator;

// Auto-install when Vue is found (browser via <script> tag)
if (typeof window !== 'undefined' && window.Vue) {
  window.Vue.use(PTMNavigatorPlugin);
}

if (process.env.NODE_ENV === 'development' && document.querySelector('#app')) {
  new Vue({
    router,
    vuetify,
    render: h => h(App),
  }).$mount('#app')
}

export default PTMNavigatorPlugin;
export { PTMNavigator };
