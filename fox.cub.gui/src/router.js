import Vue from 'vue'
import Router from 'vue-router'

import Tournaments from './views/Tournaments.vue'
import Game from './views/Game.vue'
import TeamReport from './views/TeamReport.vue'
import ManualTest from './views/ManualTest.vue'
import HowTo from './views/HowTo.vue'
import OverallMarket from './views/OverallMarket.vue'
import SingleMarket from './views/SingleMarket.vue'
import DataVisualizer from './views/DataVisualizer.vue'

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
      name: 'team_report',
      component: TeamReport,
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
    },
    {
      path: '/market',
      name: 'market',
      component: OverallMarket
    },
    {
      path: '/single_market',
      name: 'single_market',
      component: SingleMarket
    },
    {
      path: '/visualizer',
      name: 'visualizer',
      component: DataVisualizer
    }
  ]
})
