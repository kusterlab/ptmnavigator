import Vue from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify';
import vueCookie from 'vue-cookie'
import router from './router';
import 'vuetify/dist/vuetify.min.css';
import 'material-design-icons-iconfont/dist/material-design-icons.css'
import PTMNavigator from "@/components/PTMNavigator";
import 'devextreme/dist/css/dx.common.css'
import 'devextreme/dist/css/dx.material.blue.light.compact.css'


Vue.use(vueCookie)

Vue.config.productionTip = false

new Vue({
  router,
  vuetify,
  render: h => h(App),
}).$mount('#app')

//TODO: Recommended by ChatGPT, no clue if this is correct
export default {
  install(app) {
    app.component("PTMNavigator", PTMNavigator)
  }
};
