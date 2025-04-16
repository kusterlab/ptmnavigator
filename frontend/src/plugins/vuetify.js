import Vue from 'vue';
import Vuetify from 'vuetify/lib';

import ProteinIcon from '@/components/icons/ProteinIcon.vue'

Vue.use(Vuetify);

export default new Vuetify({
    theme: {
        themes: {
            light: {
                primary: '#001bc7',
                secondary: '#f0ab00'
            }
        }
    },
    icons: {
        iconfont: 'mdi',
        values: {
            protein: {
                component: ProteinIcon
            }
        }
    }
})
