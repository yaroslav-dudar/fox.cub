import Vue from 'vue'

import {
    FETCH_TOURNAMENTS,
    FETCH_PPG_TABLE,
    FETCH_HOME_ADV,
    SELECT_TOURNAMENT
} from "./actions.type";

import {
    SET_TOURNAMENTS,
    SET_SELECTED_TOURNAMENT,
    SET_PPG_TABLE,
    SET_HOME_ADV
} from "./mutations.type"

const initialState = {
    tournaments: [],
    // points-per-game table
    ppg_table: {},
    selected_tournament: '',
    home_adv: {}
};

export const state = { ...initialState };

export const actions = {
    async [FETCH_TOURNAMENTS](context) {
        let getTournametsUrl = `${Vue.config.host}/api/v1/tournament`;

        return await Vue.http.get(getTournametsUrl).then(function (response) {
            context.commit(SET_TOURNAMENTS, response.body.firstBatch);
            return response.body.firstBatch
        });
    },

    async [FETCH_PPG_TABLE](context, tournament) {
        let getPPGTableUrl = `${Vue.config.host}/api/v1/tournament/${tournament}`;

        Vue.http.get(getPPGTableUrl)
            .then(function (response) {
                context.commit(SET_PPG_TABLE, {table: response.body.table, id: tournament})
            });
    },

    async [FETCH_HOME_ADV](context, tournament) {
        let getHomeAdvUrl = `${Vue.config.host}/api/v1/tournament/home_adv/${tournament}`;

        Vue.http.get(getHomeAdvUrl)
            .then(function (response) {
                context.commit(SET_HOME_ADV, response.body.firstBatch)
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
    [SET_PPG_TABLE](state, payload) {
        state.ppg_table[payload.id] = payload.table;
    },
    [SET_HOME_ADV](state, home_adv) {
        state.home_adv = home_adv.length == 1 ? home_adv[0] : {};
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
    },
    home_adv(state) {
        return state.home_adv;
    }
};

export default {
    state,
    actions,
    mutations,
    getters
};
