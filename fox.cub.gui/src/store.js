import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    tournaments: [],
    tournament: '',
    odds: [],
    teams: []
  },
  mutations: {
    setTournaments: function(state, tournaments) {
        state.tournaments = tournaments;
    },
    setOdds: function(state, odds) {
        state.odds = odds;
    },
    setCurrentTournament: function(state, tournament) {
        state.tournament = tournament;
    }
  }
})
