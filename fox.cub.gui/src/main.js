import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store/index'

import {
  FETCH_TOURNAMENTS,
  FETCH_PPG_TABLE,
  FETCH_MARKET_TOURNAMENTS
} from "./store/actions.type";

import VueResource from 'vue-resource';
import HighchartsVue from 'highcharts-vue'

Vue.use(VueResource);
Vue.use(HighchartsVue);

Vue.config.productionTip = false
Vue.config.host = "http://localhost:8888";

new Vue({
  router,
  store,
  render: h => h(App),

  created: function () {
    store.dispatch(FETCH_MARKET_TOURNAMENTS);
    store.dispatch(FETCH_TOURNAMENTS).then(tournaments => {
      tournaments.map(t => store.dispatch(FETCH_PPG_TABLE,
                                          t._id.$oid));
    });
  }
}).$mount('#app')
