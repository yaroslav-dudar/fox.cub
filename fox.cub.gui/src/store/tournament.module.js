import Vue from 'vue'

import {
    FETCH_TOURNAMENTS,
    FETCH_PPG_TABLE,
    SELECT_TOURNAMENT
} from "./actions.type";

import {
    SET_TOURNAMENTS,
    SET_SELECTED_TOURNAMENT,
    SET_PPG_TABLE
} from "./mutations.type"

const initialState = {
    tournaments: [],
    // points-per-game table
    ppg_table: [],
    selected_tournament: ''
};

export const state = { ...initialState };

export const actions = {
    async [FETCH_TOURNAMENTS](context) {
        let getTournametsUrl = `${Vue.config.host}/api/v1/tournament`;

        Vue.http.get(getTournametsUrl).then(function (response) {
            context.commit(SET_TOURNAMENTS, response.body.firstBatch)
        });
    },

    async [FETCH_PPG_TABLE](context, tournament) {
        let getPPGTableUrl = `${Vue.config.host}/api/v1/tournament/${tournament}`;

        Vue.http.get(getPPGTableUrl)
            .then(function (response) {
                context.commit(SET_PPG_TABLE, response.body.table)
            });
    },

    [SELECT_TOURNAMENT](context, tournament) {
        context.commit(SET_SELECTED_TOURNAMENT, tournament)
    }
};

export const mutations = {
    [SET_TOURNAMENTS](state, tournaments) {
        state.tournaments = tournaments;
    },
    [SET_SELECTED_TOURNAMENT](state, tournament) {
        state.selected_tournament = tournament;
    },
    [SET_PPG_TABLE](state, ppg_table) {
        state.ppg_table = ppg_table;
    }
};

const getters = {
    tournaments(state) {
      return state.tournaments;
    },
    selected_tournament(state) {
        return state.selected_tournament;
    },
    ppg_table(state) {
        return state.ppg_table;
    }
};

export default {
    state,
    actions,
    mutations,
    getters
};
