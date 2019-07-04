import Vue from 'vue'

import {
    FETCH_ODDS
} from "./actions.type";

import {
    SET_ODDS
} from "./mutations.type"

const initialState = {
    odds: []
};

export const state = { ...initialState };

export const actions = {
    async [FETCH_ODDS](context, fixture_id) {
        let getOddsUrl = `${Vue.config.host}/api/v2/odds/${fixture_id}`;

        Vue.http.get(getOddsUrl)
            .then(function (response) {
                context.commit(SET_ODDS, response.body.firstBatch)
            });
    }
};

export const mutations = {
    [SET_ODDS](state, odds) {
        state.odds = odds;
    }
};

const getters = {
    odds(state) {
      return state.odds;
    }
};

export default {
    state,
    actions,
    mutations,
    getters
};
