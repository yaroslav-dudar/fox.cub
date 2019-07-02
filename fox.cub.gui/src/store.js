import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    tournaments: [],
    ppg_table: [],
    tournament: '',
    fixtures: [],
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
    },
    setPPGTable: function(state, ppg_table) {
      state.ppg_table = ppg_table;
    },
    setFixtures: function(state, fixtures) {
      state.fixtures = fixtures;
  },
  }
})
