import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

import VueResource from 'vue-resource';


Vue.use(VueResource);
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
    this.getTournaments().then(function(data) {
        this.$store.commit('setTournaments', data);
    })
  }
}).$mount('#app')
