import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store/index'

import { FETCH_TOURNAMENTS } from "./store/actions.type";

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
  methods: {
    getTournaments: function() {
      return this.$http.get(Vue.config.host + '/api/v1/tournament')
          .then(function (response) {
              return response.body.firstBatch;
          });
    }
  },
  created: function () {
    store.dispatch(FETCH_TOURNAMENTS);
  }
}).$mount('#app')
