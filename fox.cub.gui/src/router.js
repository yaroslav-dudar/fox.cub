import Vue from 'vue'
import Router from 'vue-router'

import Tournaments from './views/Tournaments.vue'
import Game from './views/Game.vue'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'tournaments',
      component: Tournaments
    },
    {
      path: '/game',
      name: 'game_details',
      component: Game,
      props: true
    }
  ]
})
