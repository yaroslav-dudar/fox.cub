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

export const state = { ...initialState };

export const actions = {
    async [FETCH_FIXTURES](context, tournament_id) {
        let getFixtureUrl = `${Vue.config.host}/api/v1/fixtures/${tournament_id}`;

        Vue.http.get(getFixtureUrl).then(function (response) {
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
