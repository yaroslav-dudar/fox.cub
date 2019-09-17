import Vue from 'vue'

import {
    FETCH_MARKET_TOURNAMENTS,
    FETCH_MARKET_FIXTURES
} from "./actions.type";

import {
    SET_MARKET_TOURNAMENTS,
    SET_FIXTURES
} from "./mutations.type"

const initialState = {
    market_tournaments: []
};

export const state = { ...initialState };

export const actions = {
    async [FETCH_MARKET_TOURNAMENTS](context) {
        let getTournamentsUrl = `${Vue.config.host}/api/v1/market/tournaments`;

        Vue.http.get(getTournamentsUrl).then(function (response) {
            context.commit(SET_MARKET_TOURNAMENTS, response.body.values);
        });
    },
    async [FETCH_MARKET_FIXTURES](context, tournament) {
        let getFixturesUrl = `${Vue.config.host}/api/v1/market/fixtures`;
        let params = { "tournament": tournament };

        Vue.http.get(getFixturesUrl, {params: params}).then(function (response) {
            context.commit(SET_FIXTURES, response.body.firstBatch);
        });
    },

};

export const mutations = {
    [SET_MARKET_TOURNAMENTS](state, tournaments) {
        state.market_tournaments = tournaments;
    }
};

const getters = {
    market_tournaments(state) {
      return state.market_tournaments;
    }
};

export default {
    state,
    actions,
    mutations,
    getters
};
