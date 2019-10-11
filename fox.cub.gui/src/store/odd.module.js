import Vue from 'vue'

import {
    FETCH_ODDS,
    FETCH_ODDS_DIFF
} from "./actions.type";

import {
    SET_ODDS,
    SET_ODDS_DIFF
} from "./mutations.type"

const initialState = {
    odds: [],
    odds_diff: {},
};

export const state = { ...initialState };

export const actions = {
    async [FETCH_ODDS](context, ids) {
        var getOddsUrl = `${Vue.config.host}/api/v2/odds?`;
        let fixtures = ids.map(id => `fixture_id=${id}`);
        getOddsUrl += fixtures.join('&');

        Vue.http.get(getOddsUrl)
            .then(function (response) {
                context.commit(SET_ODDS, response.body.firstBatch)
            });
    },

    async [FETCH_ODDS_DIFF](context, ids) {
        var url = `${Vue.config.host}/api/v2/odds/diff?`;
        let fixtures = ids.map(id => `fixture_id=${id}`);
        url += fixtures.join('&');

        Vue.http.get(url)
            .then(function (response) {
                context.commit(SET_ODDS_DIFF, response.body.firstBatch)
            });
    }
};

export const mutations = {
    [SET_ODDS](state, odds) {
        state.odds = odds;
    },
    [SET_ODDS_DIFF](state, odds_diff) {
        state.odds_diff = odds_diff.length > 0 ? odds_diff[0]: [];
    },
};

const getters = {
    odds(state) {
      return state.odds;
    },
    odds_diff(state) {
        return state.odds_diff;
    },
};

export default {
    state,
    actions,
    mutations,
    getters
};
