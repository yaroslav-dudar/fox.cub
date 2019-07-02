import Vue from 'vue'
import Router from 'vue-router'

import Tournaments from './views/Tournaments.vue'
import Game from './views/Game.vue'
import Team from './views/Team.vue'
import ManualTest from './views/ManualTest.vue'
import HowTo from './views/HowTo.vue'

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
    },
    {
      path: '/team',
      name: 'team_details',
      component: Team,
      props: true
    },
    {
      path: '/test',
      name: 'manual_test',
      component: ManualTest
    },
    {
      path: '/howto',
      name: 'how_to',
      component: HowTo
    }
  ]
})
