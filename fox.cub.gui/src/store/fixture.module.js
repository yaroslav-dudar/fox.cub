import Vue from 'vue'

import {
    FETCH_FIXTURES,
    SELECT_FIXTURE
} from "./actions.type";

import {
    SET_FIXTURES,
    SET_SELECTED_FIXTURE
} from "./mutations.type"

const initialState = {
    fixtures: []
};

/**
 * Return date in yyyy-mm-dd format
 */
function getDate(dayOffset) {
    var timestamp = new Date().getTime();
    var offset = 86400000 * dayOffset;
    var date = new Date(timestamp + offset);
    return date.toJSON().slice(0, 10);
}

export const state = { ...initialState };

export const actions = {
    async [FETCH_FIXTURES](context, data) {
        let getFixtureUrl = `${Vue.config.host}/api/v1/fixtures`;

        Object.keys(data).forEach((key) => (data[key] == null) && delete data[key]);

        if (!data.start) data.start = getDate(0);
        if (!data.end) data.end = getDate(10);

        Vue.http.get(getFixtureUrl, {params: data}).then(function (response) {
            context.commit(SET_FIXTURES, response.body.firstBatch);
        });
    },

    [SELECT_FIXTURE](context, fixture) {
        context.commit(SET_SELECTED_FIXTURE, fixture);
    }

};

export const mutations = {
    [SET_FIXTURES](state, fixtures) {
        state.fixtures = fixtures;
    },
    [SET_SELECTED_FIXTURE](state, fixture) {
        state.selected_fixture = fixture;
    }
};

const getters = {
    fixtures(state) {
      return state.fixtures;
    },
    selected_fixture(state) {
        return state.selected_fixture;
    }
};

export default {
    state,
    actions,
    mutations,
    getters
};
